from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, DoctorProfile, Patient, TransplantCase, Document, MedicalDecision, Notification
from app.security import require_role
from app.services.audit import log_action
from app.services import object_storage
from app.services.identity_verification import verify_identity_photos
from app.services.notifications import notify_organizer
from app.utils import to_dict, to_dict_list
from pathlib import Path
import json
import uuid
router=APIRouter(prefix="/api/v1/doctor-workflow",tags=["doctor-workflow"])
_MEDIA_TYPES={"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","pdf":"application/pdf"}

def _run_identity_check_and_notify(db,profile,doctor_user):
    """Shared with app.routers.documents -- both upload paths must trigger
    the same AI identity check and organizer notification, or a doctor
    completing registration through this endpoint instead of the other
    one would silently skip both."""
    if not (profile.photo_document_id and profile.certificate_document_id):
        return
    photo=db.query(Document).filter(Document.id==profile.photo_document_id).first()
    cert=db.query(Document).filter(Document.id==profile.certificate_document_id).first()
    if not photo or not cert:
        return
    photo_ext=Path(photo.filename).suffix.lstrip(".").lower()
    cert_ext=Path(cert.filename).suffix.lstrip(".").lower()
    if cert_ext=="pdf" or photo_ext=="pdf":
        result={"status":"not_run","same_person_likely":None,"confidence":"unknown","reasoning":"The certificate was submitted as a PDF — automated photo comparison needs an image. An organizer must review it manually."}
    else:
        result=verify_identity_photos(object_storage.read(photo.storage_path),_MEDIA_TYPES[photo_ext],object_storage.read(cert.storage_path),_MEDIA_TYPES[cert_ext])
    profile.identity_check_result=json.dumps(result)
    profile.identity_check_confidence=result.get("confidence","unknown")
    db.commit()
    name=doctor_user.full_name if doctor_user else "A doctor"
    if result.get("status")=="completed":
        if result.get("same_person_likely") is True: verdict=f"AI check: the live photo and certificate photo APPEAR TO BE THE SAME PERSON (confidence: {result.get('confidence')})."
        elif result.get("same_person_likely") is False: verdict=f"AI check: the live photo and certificate photo DO NOT APPEAR TO MATCH (confidence: {result.get('confidence')}) — please review closely, this may indicate a fraudulent submission."
        else: verdict="AI check: could not clearly determine a match from the submitted photos — manual review needed."
        detail=f"{verdict} Reasoning: {result.get('reasoning','')}"
    else:
        detail=f"AI identity check did not run ({result.get('reasoning',result.get('status'))}) — please compare the two submitted photos manually."
    notify_organizer("Q-Transplant — doctor documents ready for review",f"{name}'s license and live photo are both uploaded and ready for approval. {detail}")
class ProfileIn(BaseModel): phone:str; address:str; specialty:str; professional_information:str; hospital_id:Optional[str]=None
class DecisionIn(BaseModel): patient_id:str; decision:str; notes:Optional[str]=None
class PatientStatusIn(BaseModel): status:str

@router.get("/dashboard")
def dashboard(user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
 if not p: raise HTTPException(404,"Doctor profile not found")
 patients=db.query(Patient).filter(Patient.doctor_id==p.id).all(); cases=db.query(TransplantCase).filter(TransplantCase.hospital_id==p.hospital_id).all() if p.hospital_id else []
 return {"doctor":to_dict(p),"patients":len(patients),"waiting_patients":sum(x.waitlist_status=="waiting" for x in patients),"cases":len(cases),"notifications":db.query(Notification).filter(Notification.recipient_user_id==user.id,Notification.read==False).count()}

@router.get("/profile")
def profile(user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
 if not p: raise HTTPException(404,"Doctor profile not found")
 return to_dict(p)
@router.put("/profile")
def update_profile(body:ProfileIn,user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
 if not p: raise HTTPException(404,"Doctor profile not found")
 for k,v in body.model_dump().items(): setattr(p,k,v)
 if p.approval_status=="REQUESTED_INFO": p.approval_status="ORGANIZER_REVIEW"
 db.commit(); log_action(db,"DOCTOR_PROFILE_UPDATED",user_id=user.id,target=p.id); return to_dict(p)

@router.get("/patients")
def my_patients(user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
 if not p: raise HTTPException(404,"Doctor profile not found")
 return to_dict_list(db.query(Patient).filter(Patient.doctor_id==p.id).all())
@router.post("/patients/{patient_id}/status")
def update_patient_status(patient_id:str,body:PatientStatusIn,user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first(); patient=db.query(Patient).filter(Patient.id==patient_id).first()
 if not p or not patient or patient.doctor_id!=p.id: raise HTTPException(404,"Patient not found in your authorization scope")
 allowed={"waiting","under_review","matched","transplant_scheduled","transplant_in_progress","completed","inactive"}
 if body.status not in allowed: raise HTTPException(400,"Invalid patient status")
 patient.waitlist_status=body.status; db.commit(); log_action(db,"PATIENT_STATUS_UPDATED",user_id=user.id,target=patient_id,meta={"status":body.status}); return to_dict(patient)
@router.post("/decisions")
def record_decision(body:DecisionIn,user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first(); patient=db.query(Patient).filter(Patient.id==body.patient_id).first()
 if not p or not patient or patient.doctor_id!=p.id: raise HTTPException(403,"Not authorized for this patient")
 d=MedicalDecision(doctor_id=p.id,patient_id=patient.id,decision=body.decision,notes=body.notes); db.add(d); db.commit(); db.refresh(d); log_action(db,"MEDICAL_DECISION_RECORDED",user_id=user.id,target=patient.id,meta={"decision":body.decision}); return to_dict(d)

@router.post("/documents")
async def upload_doctor_document(kind:str=Form(...),file:UploadFile=File(...),user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 if kind not in {"profile_photo","medical_certificate","medical_report","professional_document","other"}: raise HTTPException(400,"Unsupported document kind")
 data=await file.read(10*1024*1024+1)
 if len(data)>10*1024*1024: raise HTTPException(413,"Document exceeds 10 MB")
 ext=Path(file.filename or "").suffix.lower()
 allowed_photo={".png",".jpg",".jpeg"}; allowed_doc=allowed_photo|{".pdf"}
 if ext not in (allowed_photo if kind=="profile_photo" else allowed_doc): raise HTTPException(400,"Invalid file type for this document")
 media_type={"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg","pdf":"application/pdf"}.get(ext.lstrip("."),"application/octet-stream")
 storage_ref=object_storage.save(f"{user.id}/{uuid.uuid4().hex}{ext}",data,media_type)
 d=Document(owner_user_id=user.id,kind=kind,filename=file.filename or storage_ref,storage_path=storage_ref); db.add(d); db.flush()
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
 if kind=="profile_photo": p.photo_document_id=d.id
 if kind=="medical_certificate": p.certificate_document_id=d.id
 if p.approval_status in {"PENDING_APPROVAL","REQUESTED_INFO"} and p.photo_document_id and p.certificate_document_id: p.approval_status="ORGANIZER_REVIEW"
 db.commit(); db.refresh(d); log_action(db,"DOCTOR_DOCUMENT_UPLOADED",user_id=user.id,target=d.id,meta={"kind":kind})
 _run_identity_check_and_notify(db,p,user)
 return to_dict(d)

@router.get("/documents")
def documents(user=Depends(require_role("doctor")),db:Session=Depends(get_db)): return to_dict_list(db.query(Document).filter(Document.owner_user_id==user.id).order_by(Document.uploaded_at.desc()).all())
@router.get("/cases")
def cases(user=Depends(require_role("doctor")),db:Session=Depends(get_db)):
 p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
 if not p: raise HTTPException(404,"Doctor profile not found")
 return to_dict_list(db.query(TransplantCase).join(Patient,Patient.id==TransplantCase.patient_id).filter(Patient.doctor_id==p.id).all())
