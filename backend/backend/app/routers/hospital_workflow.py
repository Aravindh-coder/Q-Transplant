from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, HospitalProfile, Patient, DoctorProfile, TransplantCase, EmergencyRequest, MatchRequest, MatchResult, DonorProfile, Document
from app.security import require_role
from app.services.audit import log_action
from app.services.notifications import notify
from app.utils import to_dict, to_dict_list
router=APIRouter(prefix="/api/v1/hospital-workflow",tags=["hospital-workflow"])
class ProfileIn(BaseModel): hospital_name:str; hospital_code:str; phone:str; address:str; location:str; registration_number:str; authorized_contact:str
class PatientIn(BaseModel): full_name:str; age:Optional[int]=None; gender:Optional[str]=None; blood_group:str; required_organ:str; doctor_id:str; hla_a:Optional[str]=None; hla_b:Optional[str]=None; hla_c:Optional[str]=None; hla_dr:Optional[str]=None; hla_dq:Optional[str]=None; urgency:str="MEDIUM"
class CaseIn(BaseModel): patient_id:str; donor_id:Optional[str]=None; stage:str="CREATED"
class StatusIn(BaseModel): stage:str

def _hospital(db,user):
 h=db.query(HospitalProfile).filter(HospitalProfile.user_id==user.id).first()
 if not h: raise HTTPException(404,"Hospital profile not found")
 if h.verification_status.lower() not in {"verified","approved"}: raise HTTPException(403,"Hospital account is awaiting organizer verification")
 return h
@router.get("/dashboard")
def dashboard(user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); return {"hospital":to_dict(h),"doctors":db.query(DoctorProfile).filter(DoctorProfile.hospital_id==h.id).count(),"patients":db.query(Patient).filter(Patient.hospital_id==h.id).count(),"cases":db.query(TransplantCase).filter(TransplantCase.hospital_id==h.id).count(),"emergencies":db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id==h.id).count(),"matching_requests":db.query(MatchRequest).filter(MatchRequest.requested_by==user.id).count()}
@router.get("/profile")
def profile(user=Depends(require_role("hospital")),db:Session=Depends(get_db)): return to_dict(_hospital(db,user))
@router.put("/profile")
def update_profile(body:ProfileIn,user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user)
 for k,v in body.dict().items(): setattr(h,k,v)
 db.commit(); return to_dict(h)
@router.get("/doctors")
def doctors(user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); return to_dict_list(db.query(DoctorProfile).filter(DoctorProfile.hospital_id==h.id).all())
@router.get("/patients")
def patients(user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); return to_dict_list(db.query(Patient).filter(Patient.hospital_id==h.id).all())
@router.post("/patients")
def create_patient(body:PatientIn,user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); d=db.query(DoctorProfile).filter(DoctorProfile.id==body.doctor_id,DoctorProfile.hospital_id==h.id,DoctorProfile.approval_status.in_(["APPROVED","approved"])).first()
 if not d: raise HTTPException(400,"Select an approved doctor associated with this hospital")
 data=body.dict(); data.pop("doctor_id"); p=Patient(hospital_id=h.id,doctor_id=d.id,**data); db.add(p); db.commit(); db.refresh(p); log_action(db,"HOSPITAL_PATIENT_CREATED",user_id=user.id,target=p.id); return to_dict(p)
@router.get("/cases")
def cases(user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); return to_dict_list(db.query(TransplantCase).filter(TransplantCase.hospital_id==h.id).all())
@router.post("/cases")
def create_case(body:CaseIn,user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); p=db.query(Patient).filter(Patient.id==body.patient_id,Patient.hospital_id==h.id).first()
 if not p: raise HTTPException(404,"Patient not found in this hospital")
 c=TransplantCase(patient_id=p.id,hospital_id=h.id,donor_id=body.donor_id,stage=body.stage); db.add(c); db.commit(); db.refresh(c); log_action(db,"TRANSPLANT_CASE_CREATED",user_id=user.id,target=c.id); return to_dict(c)
@router.patch("/cases/{case_id}")
def update_case(case_id:str,body:StatusIn,user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); c=db.query(TransplantCase).filter(TransplantCase.id==case_id,TransplantCase.hospital_id==h.id).first()
 if not c: raise HTTPException(404,"Case not found")
 allowed={"CREATED","MATCHING","DONOR_ACCEPTED","APPROVED","SCHEDULED","IN_PROGRESS","COMPLETED","CANCELLED","REJECTED"}
 if body.stage not in allowed: raise HTTPException(400,"Invalid case stage")
 c.stage=body.stage; db.commit(); log_action(db,"TRANSPLANT_CASE_UPDATED",user_id=user.id,target=case_id,meta={"stage":body.stage}); return to_dict(c)
@router.get("/documents")
def documents(user=Depends(require_role("hospital")),db:Session=Depends(get_db)):
 h=_hospital(db,user); ids=[p.id for p in db.query(Patient).filter(Patient.hospital_id==h.id).all()]
 # Hospital may view only documents owned by its authorized users; donor documents are never exposed here.
 return {"hospital_documents":to_dict_list(db.query(Document).filter(Document.owner_user_id==user.id).all()),"patient_ids":ids}
