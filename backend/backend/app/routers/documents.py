import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document
from app.security import get_current_user
from app.services.audit import log_action
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()
ALLOWED = {"pdf", "png", "jpg", "jpeg"}
MAX_BYTES = 10 * 1024 * 1024

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
