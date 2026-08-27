from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Patient, DoctorProfile
from app.security import require_role
from app.services.audit import log_action
from app.services.urgency import calculate_priority
from app.utils import to_dict, to_dict_list
router=APIRouter(prefix="/api/v1/patients",tags=["patients"])
class PatientIn(BaseModel):
    full_name:str; age:Optional[int]=None; gender:Optional[str]=None; blood_group:str; required_organ:str
    hla_a:Optional[str]=None; hla_b:Optional[str]=None; hla_c:Optional[str]=None; hla_dr:Optional[str]=None; hla_dq:Optional[str]=None; urgency:str="MEDIUM"

def _doctor(db,user):
    d=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
    if not d or d.approval_status.upper()!="APPROVED": raise HTTPException(403,"Only an organizer-approved doctor can access patient records.")
    return d
@router.post("")
def create_patient(body:PatientIn,user:User=Depends(require_role("doctor")),db:Session=Depends(get_db)):
    doctor=_doctor(db,user)
    if not doctor.hospital_id: raise HTTPException(400,"Your doctor profile isn't linked to a hospital yet.")
    if body.age is not None and not 0<body.age<130: raise HTTPException(400,"Invalid patient age")
    patient=Patient(hospital_id=doctor.hospital_id,doctor_id=doctor.id,**body.dict()); db.add(patient); db.commit(); db.refresh(patient); log_action(db,"PATIENT_CREATED",user_id=user.id,target=patient.id); return to_dict(patient)
@router.get("")
def list_my_patients(user:User=Depends(require_role("doctor")),db:Session=Depends(get_db)):
    doctor=_doctor(db,user); patients=db.query(Patient).filter(Patient.doctor_id==doctor.id).all()
    for p in patients: p.priority_score=calculate_priority(p.urgency,p.waiting_since)["score"]
    db.commit(); return to_dict_list(patients)
@router.get("/{patient_id}")
def get_patient(patient_id:str,user:User=Depends(require_role("doctor","hospital","organizer")),db:Session=Depends(get_db)):
    patient=db.query(Patient).filter(Patient.id==patient_id).first()
    if not patient: raise HTTPException(404,"Patient not found.")
    if user.role=="doctor":
        d=_doctor(db,user)
        if patient.doctor_id!=d.id: raise HTTPException(403,"Not authorized for this patient")
    elif user.role=="hospital":
        from app.models import HospitalProfile
        h=db.query(HospitalProfile).filter(HospitalProfile.user_id==user.id).first()
        if not h or patient.hospital_id!=h.id: raise HTTPException(403,"Not authorized for this patient")
    return to_dict(patient)
