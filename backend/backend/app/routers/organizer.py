from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User, DoctorProfile, DonorProfile, HospitalProfile, Patient, TransplantCase, AuditLog, EmergencyRequest, MatchRequest, MatchResult, Document
from app.security import require_role
from app.services.audit import log_action
from app.services.notifications import notify
from app.utils import to_dict, to_dict_list
router=APIRouter(prefix="/api/v1/organizer",tags=["organizer"])
class InfoRequest(BaseModel): message:str
@router.get("/doctors/pending")
def pending_doctors(user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    return to_dict_list(db.query(DoctorProfile).filter(DoctorProfile.approval_status.in_(["PENDING_APPROVAL","ORGANIZER_REVIEW","pending"])).all())
@router.get("/doctors/{doctor_id}/review")
def review_doctor(doctor_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
    if not d: raise HTTPException(404,"Doctor not found")
    account=db.query(User).filter(User.id==d.user_id).first()
    docs=db.query(Document).filter(Document.owner_user_id==d.user_id).all()
    d.approval_status="ORGANIZER_REVIEW"; db.commit()
    return {"doctor":to_dict(d),"account":to_dict(account),"documents":to_dict_list(docs)}
@router.post("/doctors/{doctor_id}/request-info")
def request_info(doctor_id,body:InfoRequest,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
    if not d: raise HTTPException(404,"Doctor not found")
    d.approval_status="PENDING_INFORMATION"; account=db.query(User).filter(User.id==d.user_id).first(); db.commit()
    notify(db,account,"Additional information required",body.message,priority="high",also_email=True); log_action(db,"DOCTOR_INFO_REQUESTED",user_id=user.id,target=doctor_id,meta={"message":body.message})
    return {"status":d.approval_status}
@router.post("/doctors/{doctor_id}/approve")
def approve_doctor(doctor_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
    if not d: raise HTTPException(404,"Doctor not found")
    if not d.photo_document_id or not d.certificate_document_id: raise HTTPException(400,"Mandatory profile photo and medical certificate must be uploaded before approval.")
    d.approval_status="APPROVED"; account=db.query(User).filter(User.id==d.user_id).first(); account.status="active"; db.commit()
    notify(db,account,"Doctor registration approved","Your Q-Transplant doctor account is approved. You can now access the doctor portal.",priority="high",also_email=True); log_action(db,"DOCTOR_APPROVED",user_id=user.id,target=doctor_id); return {"id":d.id,"approval_status":d.approval_status}
@router.post("/doctors/{doctor_id}/reject")
def reject_doctor(doctor_id,reason:str="",user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
    if not d: raise HTTPException(404,"Doctor not found")
    d.approval_status="REJECTED"; account=db.query(User).filter(User.id==d.user_id).first(); account.status="suspended"; db.commit(); notify(db,account,"Doctor registration rejected",reason or "Your registration was rejected by the organizer.",priority="high",also_email=True); log_action(db,"DOCTOR_REJECTED",user_id=user.id,target=doctor_id,meta={"reason":reason}); return {"id":d.id,"approval_status":d.approval_status}
@router.post("/hospitals/{hospital_id}/verify")
def verify_hospital(hospital_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    h=db.query(HospitalProfile).filter(HospitalProfile.id==hospital_id).first()
    if not h: raise HTTPException(404,"Hospital not found")
    h.verification_status="verified"; a=db.query(User).filter(User.id==h.user_id).first(); a.status="active"; db.commit(); log_action(db,"HOSPITAL_VERIFIED",user_id=user.id,target=hospital_id); return {"id":h.id,"verification_status":h.verification_status}
@router.post("/users/{target_user_id}/suspend")
def suspend_user(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    a=db.query(User).filter(User.id==target_user_id).first()
    if not a: raise HTTPException(404,"User not found")
    a.status="suspended"; db.commit(); log_action(db,"ACCOUNT_SUSPENDED",user_id=user.id,target=target_user_id); return {"id":a.id,"status":a.status}
@router.post("/users/{target_user_id}/reactivate")
def reactivate_user(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    a=db.query(User).filter(User.id==target_user_id).first()
    if not a: raise HTTPException(404,"User not found")
    a.status="active"; db.commit(); log_action(db,"ACCOUNT_REACTIVATED",user_id=user.id,target=target_user_id); return {"id":a.id,"status":a.status}
@router.get("/users")
def users(user=Depends(require_role("organizer")),db:Session=Depends(get_db)): return to_dict_list(db.query(User).order_by(User.created_at.desc()).all())
@router.get("/cases")
def cases(user=Depends(require_role("organizer")),db:Session=Depends(get_db)): return to_dict_list(db.query(TransplantCase).all())
@router.get("/emergencies")
def emergencies(user=Depends(require_role("organizer")),db:Session=Depends(get_db)): return to_dict_list(db.query(EmergencyRequest).order_by(EmergencyRequest.created_at.desc()).all())
@router.get("/matching-requests")
def matching_requests(user=Depends(require_role("organizer")),db:Session=Depends(get_db)): return to_dict_list(db.query(MatchRequest).order_by(MatchRequest.created_at.desc()).all())
@router.get("/stats")
def stats(user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
    return {"total_donors":db.query(DonorProfile).count(),"active_donors":db.query(DonorProfile).filter(DonorProfile.availability_status=="active").count(),"total_recipients":db.query(Patient).count(),"active_transplant_cases":db.query(TransplantCase).filter(~TransplantCase.stage.in_(["COMPLETED","CANCELLED","REJECTED"])).count(),"registered_hospitals":db.query(HospitalProfile).count(),"approved_doctors":db.query(DoctorProfile).filter(DoctorProfile.approval_status=="APPROVED").count(),"pending_doctors":db.query(DoctorProfile).filter(DoctorProfile.approval_status.in_(["PENDING_APPROVAL","ORGANIZER_REVIEW","PENDING_INFORMATION","pending"])).count(),"emergency_requests":db.query(EmergencyRequest).filter(EmergencyRequest.status.notin_(["RESOLVED","COMPLETED"])).count(),"matching_requests":db.query(MatchRequest).count(),"successful_matches":db.query(MatchResult).count(),"completed_transplant_cases":db.query(TransplantCase).filter(TransplantCase.stage=="COMPLETED").count()}
@router.get("/audit-log")
def audit_log(limit:int=100,user=Depends(require_role("organizer")),db:Session=Depends(get_db)): return to_dict_list(db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all())
