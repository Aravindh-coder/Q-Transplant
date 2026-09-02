from typing import Optional
import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DonorProfile, Document
from app.security import require_role, hash_password
from app.services.audit import log_action
from app.services.search_service import paginate
from app.services.performance import bounded_page, DEFAULT_PAGE_SIZE
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/donors", tags=["donors"])
DONATION_STATUSES = {"ACTIVE", "UNDER REVIEW", "MATCHED", "DONATION IN PROCESS", "COMPLETED", "INACTIVE"}
VALID_BLOOD_GROUPS = {"O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"}
MAX_IMPORT_ROWS = 5000


class DonorProfileIn(BaseModel):
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: str
    organs_available: list[str] = Field(default_factory=list)
    hla_a: Optional[str] = None
    hla_b: Optional[str] = None
    hla_c: Optional[str] = None
    hla_dr: Optional[str] = None
    hla_dq: Optional[str] = None
    medical_information: Optional[str] = None


class DonationStatusIn(BaseModel):
    status: str


@router.put("/me")
def upsert_my_profile(body: DonorProfileIn, user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        profile = DonorProfile(user_id=user.id, blood_group=body.blood_group.upper(), donation_status="ACTIVE")
        db.add(profile)
    data = body.model_dump(exclude_unset=True)
    data["blood_group"] = body.blood_group.upper()
    for field, value in data.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    log_action(db, "DONOR_PROFILE_UPDATED", user_id=user.id)
    return to_dict(profile)


@router.get("/me")
def get_my_profile(user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No donor profile yet — PUT /donors/me to create one.")
    return to_dict(profile)


@router.get("/me/status")
def get_my_status(user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No donor profile yet.")
    return {"availability_status": profile.availability_status, "donation_status": profile.donation_status,
            "verification_status": profile.verification_status}


@router.post("/me/availability")
def set_availability(active: bool, user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No donor profile yet.")
    profile.availability_status = "active" if active else "inactive"
    if not active and profile.donation_status == "ACTIVE":
        profile.donation_status = "INACTIVE"
    elif active and profile.donation_status == "INACTIVE":
        profile.donation_status = "ACTIVE"
    db.commit()
    log_action(db, "DONOR_AVAILABILITY_CHANGED", user_id=user.id, target=profile.availability_status)
    return {"availability_status": profile.availability_status, "donation_status": profile.donation_status}


@router.get("/me/documents")
def my_documents(user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.owner_user_id == user.id).order_by(Document.uploaded_at.desc()).all()
    return to_dict_list(docs)


@router.patch("/{donor_id}/status")
def update_donation_status(donor_id: str, body: DonationStatusIn,
                           user: User = Depends(require_role("doctor", "hospital", "organizer")),
                           db: Session = Depends(get_db)):
    status = body.status.upper()
    if status not in DONATION_STATUSES:
        raise HTTPException(400, f"status must be one of: {', '.join(sorted(DONATION_STATUSES))}")
    profile = db.query(DonorProfile).filter(DonorProfile.id == donor_id).first()
    if not profile:
        raise HTTPException(404, "Donor not found.")
    profile.donation_status = status
    if status == "INACTIVE":
        profile.availability_status = "inactive"
    elif status in {"ACTIVE", "UNDER REVIEW", "MATCHED", "DONATION IN PROCESS"}:
        profile.availability_status = "active"
    db.commit()
    log_action(db, "DONOR_DONATION_STATUS_CHANGED", user_id=user.id, target=donor_id, meta={"status": status})
    return {"donor_id": donor_id, "donation_status": status, "availability_status": profile.availability_status}


@router.get("/search")
def search_donors(organ: Optional[str] = None, blood_group: Optional[str] = None,
                 page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                 user: User = Depends(require_role("doctor", "hospital", "organizer")),
                 db: Session = Depends(get_db)):
    page, page_size = bounded_page(page, page_size)
    q = db.query(DonorProfile).filter(DonorProfile.availability_status == "active")
    if blood_group:
        q = q.filter(DonorProfile.blood_group == blood_group.upper())
    if organ:
        # organs_available is a JSON column, so this filter can't run in SQL
        # portably across SQLite/Postgres -- bounded pre-fetch keeps this
        # from ever loading an unbounded table into memory.
        candidates = q.limit(2000).all()
        results = [d for d in candidates if any(o.replace("_partial", "") == organ.lower() for o in (d.organs_available or []))]
        total = len(results)
        page_items = results[(page - 1) * page_size: page * page_size]
        return {"items": to_dict_list(page_items, exclude={"medical_information"}), "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size}
    paginated = paginate(q, page, page_size)
    return {**paginated, "items": to_dict_list(paginated["items"], exclude={"medical_information"})}


@router.post("/import")
async def import_donors_csv(file: UploadFile = File(...),
                             user: User = Depends(require_role("doctor", "hospital", "organizer")),
                             db: Session = Depends(get_db)):
    """Bulk-import a donor dataset from a CSV file. Deliberately not
    available to the donor role -- this creates OTHER people's records in
    bulk, which is an operational/administrative action, not something a
    donor account should be able to do to itself or others.

    Expected columns (case-insensitive, extra columns ignored):
    full_name, email, blood_group (required), organs_available (comma or
    semicolon separated, e.g. "kidney;liver"), hla_a, hla_b, hla_c, hla_dr,
    hla_dq, phone, address, date_of_birth, gender.

    Every row shares one bcrypt hash for its placeholder login password --
    hashing per-row was the exact bug that made seed_donors.py take
    unreasonably long for a dataset this size; this avoids repeating it.
    """
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(400, "Only .csv files are accepted.")
    raw = await file.read(10 * 1024 * 1024 + 1)
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(413, "Import file exceeds the 10 MB limit.")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(400, "File must be UTF-8 encoded CSV.")

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(400, "CSV has no header row.")
    fieldmap = {name.strip().lower(): name for name in reader.fieldnames}
    if "blood_group" not in fieldmap:
        raise HTTPException(400, "CSV must include a \'blood_group\' column.")

    rows = list(reader)
    if len(rows) > MAX_IMPORT_ROWS:
        raise HTTPException(400, f"Import capped at {MAX_IMPORT_ROWS} rows per file; split into multiple imports.")

    shared_password_hash = hash_password(uuid.uuid4().hex)  # random, unusable placeholder -- these accounts are records, not logins anyone is meant to use directly
    created, skipped = 0, []

    for i, row in enumerate(rows, start=2):  # start=2: row 1 is the header
        def get(col):
            key = fieldmap.get(col)
            return (row.get(key) or "").strip() if key else ""

        blood_group = get("blood_group").upper()
        if blood_group not in VALID_BLOOD_GROUPS:
            skipped.append({"row": i, "reason": f"invalid or missing blood_group: {blood_group!r}"})
            continue

        email = get("email") or f"import-{uuid.uuid4().hex[:12]}@donors.qtransplant.local"
        if db.query(User).filter(User.email == email).first():
            skipped.append({"row": i, "reason": f"email already exists: {email}"})
            continue

        organs_raw = get("organs_available")
        organs = [o.strip().lower() for o in organs_raw.replace(";", ",").split(",") if o.strip()]

        u = User(email=email, hashed_password=shared_password_hash, role="donor",
                  full_name=get("full_name") or "Imported Donor", status="active", email_verified=True)
        db.add(u)
        db.flush()
        db.add(DonorProfile(
            user_id=u.id, blood_group=blood_group, organs_available=organs,
            date_of_birth=get("date_of_birth") or None, gender=get("gender") or None,
            phone=get("phone") or None, address=get("address") or None,
            hla_a=get("hla_a") or None, hla_b=get("hla_b") or None, hla_c=get("hla_c") or None,
            hla_dr=get("hla_dr") or None, hla_dq=get("hla_dq") or None,
            availability_status="active", donation_status="ACTIVE", verification_status="pending",
        ))
        created += 1

    db.commit()
    log_action(db, "DONORS_IMPORTED", user_id=user.id, meta={"created": created, "skipped": len(skipped), "rows": len(rows)})
    return {"rows_processed": len(rows), "created": created, "skipped_count": len(skipped), "skipped": skipped[:50]}
