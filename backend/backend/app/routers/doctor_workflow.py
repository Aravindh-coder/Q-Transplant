from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, DoctorProfile, Patient, HospitalProfile, Document, MedicalDecision, TransplantCase, Notification
from app.security import require_role
from app.services.notifications import notify
from app.services.audit import log_action
from app.utils import to_dict, to_dict_list
from pathlib import Path
import os, uuid

router = APIRouter(prefix="/api/v1/doctor-workflow", tags=["doctor-workflow"])
UPLOAD_ROOT = Path(os.getenv("UPLOAD_DIR", "uploads")).resolve()

class DecisionIn(BaseModel):
    patient_id: str
    decision: str
    notes: Optional[str] = None

class PatientStatusIn(BaseModel):
    status: str

@router.get("/dashboard")
def dashboard(user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    p = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
    if not p: raise HTTPException(404, "Doctor profile not found")
    patients = db.query(Patient).filter(Patient.doctor_id == p.id).all()
    cases = db.query(TransplantCase).filter(TransplantCase.hospital_id == p.hospital_id).all() if p.hospital_id else []
    return {"doctor": to_dict(p), "patients": len(patients), "waiting_patients": sum(x.waitlist_status == "waiting" for x in patients), "cases": len(cases), "notifications": db.query(Notification).filter(Notification.recipient_user_id == user.id, Notification.read == False).count()}

@router.get("/patients")
def my_patients(user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    p = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
    if not p: raise HTTPException(404, "Doctor profile not found")
    return to_dict_list(db.query(Patient).filter(Patient.doctor_id == p.id).all())

@router.post("/patients/{patient_id}/status")
def update_patient_status(patient_id: str, body: PatientStatusIn, user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    p = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first(); patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not p or not patient or patient.doctor_id != p.id: raise HTTPException(404, "Patient not found in your authorization scope")
    allowed = {"waiting", "under_review", "matched", "transplant_scheduled", "transplant_in_progress", "completed", "inactive"}
    if body.status not in allowed: raise HTTPException(400, "Invalid patient status")
    patient.waitlist_status = body.status; db.commit(); log_action(db, "PATIENT_STATUS_UPDATED", user_id=user.id, target=patient_id, meta={"status": body.status})
    return to_dict(patient)

@router.post("/decisions")
def record_decision(body: DecisionIn, user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    p = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first(); patient = db.query(Patient).filter(Patient.id == body.patient_id).first()
    if not p or not patient or patient.doctor_id != p.id: raise HTTPException(403, "Not authorized for this patient")
    d = MedicalDecision(doctor_id=p.id, patient_id=patient.id, decision=body.decision, notes=body.notes)
    db.add(d); db.commit(); db.refresh(d); log_action(db, "MEDICAL_DECISION_RECORDED", user_id=user.id, target=patient.id, meta={"decision": body.decision})
    return to_dict(d)

@router.post("/documents")
async def upload_doctor_document(kind: str = Form(...), file: UploadFile = File(...), user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    data = await file.read(10 * 1024 * 1024 + 1)
    if len(data) > 10 * 1024 * 1024: raise HTTPException(413, "Document exceeds 10 MB")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".pdf", ".png", ".jpg", ".jpeg"}: raise HTTPException(400, "Only PDF, PNG and JPEG files are allowed")
    folder = UPLOAD_ROOT / user.id; folder.mkdir(parents=True, exist_ok=True); path = folder / f"{uuid.uuid4().hex}{ext}"; path.write_bytes(data)
    d = Document(owner_user_id=user.id, kind=kind, filename=file.filename or path.name, storage_path=str(path)); db.add(d); db.commit(); db.refresh(d); return to_dict(d)

@router.get("/cases")
def cases(user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    p = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
    if not p: raise HTTPException(404, "Doctor profile not found")
    return to_dict_list(db.query(TransplantCase).join(Patient, Patient.id == TransplantCase.patient_id).filter(Patient.doctor_id == p.id).all())
