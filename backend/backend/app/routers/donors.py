from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DonorProfile, Document
from app.security import require_role
from app.services.audit import log_action
from app.services.search_service import paginate
from app.services.performance import bounded_page, DEFAULT_PAGE_SIZE
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/donors", tags=["donors"])
DONATION_STATUSES = {"ACTIVE", "UNDER REVIEW", "MATCHED", "DONATION IN PROCESS", "COMPLETED", "INACTIVE"}


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
    data = body.dict(exclude_unset=True)
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
