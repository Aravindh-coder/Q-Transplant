import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document, DoctorProfile, HospitalProfile
from app.security import get_current_user
from app.services.audit import log_action
from app.services.identity_verification import verify_identity_photos
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
ALLOWED = {"pdf", "png", "jpg", "jpeg"}
MAX_BYTES = 10 * 1024 * 1024
_MEDIA_TYPES = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "pdf": "application/pdf"}
# kind values the frontend can send, normalized to what gets linked where
_PHOTO_KINDS = {"photo", "live_photo", "selfie"}
_CERT_KINDS = {"certificate", "license", "license_certificate"}


def _run_identity_check_if_ready(db: Session, profile: DoctorProfile):
    if not (profile.photo_document_id and profile.certificate_document_id):
        return
    photo = db.query(Document).filter(Document.id == profile.photo_document_id).first()
    cert = db.query(Document).filter(Document.id == profile.certificate_document_id).first()
    if not photo or not cert:
        return
    photo_ext = Path(photo.storage_path).suffix.lstrip(".")
    cert_ext = Path(cert.storage_path).suffix.lstrip(".")
    if cert_ext == "pdf" or photo_ext == "pdf":
        # The comparison model takes images, not PDFs — skip automatically
        # and let the organizer compare visually instead.
        result = {"status": "not_run", "same_person_likely": None, "confidence": "unknown",
                  "reasoning": "The certificate was submitted as a PDF — automated photo comparison needs an image. An organizer must review it manually."}
    else:
        result = verify_identity_photos(
            Path(photo.storage_path).read_bytes(), _MEDIA_TYPES[photo_ext],
            Path(cert.storage_path).read_bytes(), _MEDIA_TYPES[cert_ext],
        )
    import json
    profile.identity_check_result = json.dumps(result)
    profile.identity_check_confidence = result.get("confidence", "unknown")
    db.commit()


@router.post("")
async def upload_document(kind: str, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ext = Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in ALLOWED:
        raise HTTPException(400, "Only PDF, PNG and JPEG documents are allowed.")
    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Document exceeds the 10 MB limit.")
    owner_dir = UPLOAD_ROOT / user.id
    owner_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    path = owner_dir / safe_name
    path.write_bytes(data)
    doc = Document(owner_user_id=user.id, kind=kind, filename=file.filename or safe_name, storage_path=str(path))
    db.add(doc); db.commit(); db.refresh(doc)
    log_action(db, "DOCUMENT_UPLOADED", user_id=user.id, target=doc.id, meta={"kind": kind})

    # Auto-link to the owning profile so the organizer approval check
    # (which requires both IDs to be set) can ever actually be satisfied.
    if user.role == "doctor" and kind in (_PHOTO_KINDS | _CERT_KINDS):
        profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
        if profile:
            if kind in _PHOTO_KINDS:
                profile.photo_document_id = doc.id
            else:
                profile.certificate_document_id = doc.id
            db.commit()
            _run_identity_check_if_ready(db, profile)
    elif user.role == "hospital" and kind in _CERT_KINDS:
        profile = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        if profile:
            profile.license_document_id = doc.id
            db.commit()

    return to_dict(doc)

@router.get("/me")
def my_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return to_dict_list(db.query(Document).filter(Document.owner_user_id == user.id).order_by(Document.uploaded_at.desc()).all())

@router.get("/{document_id}")
def document_metadata(document_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found.")
    if doc.owner_user_id != user.id and user.role != "organizer":
        raise HTTPException(403, "Not authorized to access this document.")
    return to_dict(doc)

@router.get("/{document_id}/file")
def document_file(document_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found.")
    if doc.owner_user_id != user.id and user.role != "organizer":
        raise HTTPException(403, "Not authorized to access this document.")
    path = Path(doc.storage_path)
    if not path.is_file():
        raise HTTPException(404, "Stored file is missing.")
    ext = path.suffix.lstrip(".")
    return FileResponse(path, media_type=_MEDIA_TYPES.get(ext, "application/octet-stream"), filename=doc.filename)
