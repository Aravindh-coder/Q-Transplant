from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, DoctorProfile, DonorProfile, HospitalProfile, Patient, TransplantCase, AuditLog, MatchRequest, MatchResult, EmergencyRequest, Document
from app.security import require_role
from app.services.audit import log_action
from app.services.notifications import notify
from app.services.search_service import paginate
from app.services.performance import bounded_page, DEFAULT_PAGE_SIZE
from app.utils import to_dict, to_dict_list
router=APIRouter(prefix="/api/v1/organizer",tags=["organizer"])

def _doctor_review(db,doctor):
 account=db.query(User).filter(User.id==doctor.user_id).first(); docs=db.query(Document).filter(Document.owner_user_id==doctor.user_id).all()
 return {"doctor":to_dict(doctor),"user":to_dict(account),"documents":to_dict_list(docs),"photo_submitted":bool(doctor.photo_document_id),"certificate_submitted":bool(doctor.certificate_document_id)}
@router.get("/doctors/pending")
def pending_doctors(user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 return [_doctor_review(db,d) for d in db.query(DoctorProfile).filter(DoctorProfile.approval_status.in_(["pending","PENDING_APPROVAL","ORGANIZER_REVIEW","REQUESTED_INFO"])).all()]
@router.get("/doctors/{doctor_id}/review")
def review_doctor(doctor_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
 if not d: raise HTTPException(404,"Doctor not found")
 return _doctor_review(db,d)
@router.post("/doctors/{doctor_id}/approve")
def approve_doctor(doctor_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
 if not d: raise HTTPException(404,"Doctor profile not found")
 if not d.photo_document_id or not d.certificate_document_id: raise HTTPException(400,"Doctor photo and medical certificate are mandatory before approval")
 d.approval_status="APPROVED"; account=db.query(User).filter(User.id==d.user_id).first(); account.status="active"; account.email_verified=True; db.commit(); notify(db,account,"Doctor account approved","Your doctor account has been approved.",priority="high",also_email=True); log_action(db,"DOCTOR_APPROVED",user_id=user.id,target=doctor_id); return {"id":d.id,"approval_status":d.approval_status}
@router.post("/doctors/{doctor_id}/reject")
def reject_doctor(doctor_id,reason="",user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
 if not d: raise HTTPException(404,"Doctor profile not found")
 d.approval_status="REJECTED"; a=db.query(User).filter(User.id==d.user_id).first(); a.status="rejected"; db.commit(); notify(db,a,"Doctor registration rejected",f"Your registration was rejected. {reason}".strip(),priority="high",also_email=True); log_action(db,"DOCTOR_REJECTED",user_id=user.id,target=doctor_id,meta={"reason":reason}); return {"id":d.id,"approval_status":d.approval_status}
@router.post("/doctors/{doctor_id}/request-information")
def request_doctor_information(doctor_id,message="Please provide the requested additional information.",user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DoctorProfile).filter(DoctorProfile.id==doctor_id).first()
 if not d: raise HTTPException(404,"Doctor profile not found")
 d.approval_status="REQUESTED_INFO"; a=db.query(User).filter(User.id==d.user_id).first(); db.commit(); notify(db,a,"Additional information required",message,priority="high",also_email=True); log_action(db,"DOCTOR_INFO_REQUESTED",user_id=user.id,target=doctor_id,meta={"message":message}); return {"id":doctor_id,"approval_status":d.approval_status}
@router.post("/hospitals/{hospital_id}/verify")
def verify_hospital(hospital_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 h=db.query(HospitalProfile).filter(HospitalProfile.id==hospital_id).first()
 if not h: raise HTTPException(404,"Hospital not found")
 if not h.license_document_id: raise HTTPException(400,"Hospital must submit a registration/license document before verification.")
 h.verification_status="verified"; a=db.query(User).filter(User.id==h.user_id).first(); a.status="active"; a.email_verified=True; db.commit(); notify(db,a,"Hospital verification approved","Your hospital account is verified.",priority="high",also_email=True); log_action(db,"HOSPITAL_VERIFIED",user_id=user.id,target=hospital_id); return {"id":h.id,"verification_status":h.verification_status}

def _donor_review(db,donor):
 account=db.query(User).filter(User.id==donor.user_id).first()
 doc=db.query(Document).filter(Document.id==donor.medical_document_id).first() if donor.medical_document_id else None
 return {"donor":to_dict(donor,exclude={"phone","address","date_of_birth","gender"}),"user":{"id":account.id,"full_name":account.full_name,"email":account.email} if account else None,"medical_document":to_dict(doc),"document_submitted":bool(donor.medical_document_id)}
@router.get("/donors/pending")
def pending_donors(user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 return [_donor_review(db,d) for d in db.query(DonorProfile).filter(DonorProfile.verification_status.in_(["pending","under_review"])).all()]
@router.get("/donors/{donor_id}/review")
def review_donor(donor_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DonorProfile).filter(DonorProfile.id==donor_id).first()
 if not d: raise HTTPException(404,"Donor not found")
 return _donor_review(db,d)
@router.post("/donors/{donor_id}/verify")
def verify_donor(donor_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DonorProfile).filter(DonorProfile.id==donor_id).first()
 if not d: raise HTTPException(404,"Donor not found")
 if not d.medical_document_id: raise HTTPException(400,"Donor must submit a medical document before verification.")
 if not d.hospital_id: raise HTTPException(400,"Donor must be linked to a verified hospital before verification -- this is what appears in search results in place of the donor's own identity.")
 d.verification_status="verified"; account=db.query(User).filter(User.id==d.user_id).first()
 db.commit(); notify(db,account,"Donor account verified","Your donor profile has been verified and is now visible in hospital searches.",priority="high",also_email=True); log_action(db,"DONOR_VERIFIED",user_id=user.id,target=donor_id); return {"id":d.id,"verification_status":d.verification_status}
@router.post("/donors/{donor_id}/reject")
def reject_donor(donor_id,reason="",user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 d=db.query(DonorProfile).filter(DonorProfile.id==donor_id).first()
 if not d: raise HTTPException(404,"Donor not found")
 d.verification_status="rejected"; account=db.query(User).filter(User.id==d.user_id).first()
 db.commit(); notify(db,account,"Donor verification rejected",f"Your donor registration was rejected. {reason}".strip(),priority="high",also_email=True); log_action(db,"DONOR_REJECTED",user_id=user.id,target=donor_id,meta={"reason":reason}); return {"id":d.id,"verification_status":d.verification_status}
@router.get("/users")
def users(role:str|None=None,search:str|None=None,page:int=1,page_size:int=DEFAULT_PAGE_SIZE,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 page,page_size=bounded_page(page,page_size)
 q=db.query(User)
 if role: q=q.filter(User.role==role)
 if search: q=q.filter((User.email.ilike(f"%{search}%"))|(User.full_name.ilike(f"%{search}%")))
 paginated=paginate(q.order_by(User.created_at.desc()),page,page_size)
 return {**paginated,"items":to_dict_list(paginated["items"])}
@router.post("/users/{target_user_id}/activate")
def activate_user(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 t=db.query(User).filter(User.id==target_user_id).first()
 if not t: raise HTTPException(404,"User not found")
 t.status="active"; db.commit(); log_action(db,"ACCOUNT_ACTIVATED",user_id=user.id,target=t.id); return {"id":t.id,"status":t.status}
@router.post("/users/{target_user_id}/deactivate")
def deactivate_user(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 t=db.query(User).filter(User.id==target_user_id).first()
 if not t: raise HTTPException(404,"User not found")
 t.status="inactive"; db.commit(); log_action(db,"ACCOUNT_DEACTIVATED",user_id=user.id,target=t.id); return {"id":t.id,"status":t.status}
@router.post("/users/{target_user_id}/suspend")
def suspend_user(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 t=db.query(User).filter(User.id==target_user_id).first()
 if not t: raise HTTPException(404,"User not found")
 t.status="suspended"; db.commit(); log_action(db,"ACCOUNT_SUSPENDED",user_id=user.id,target=t.id); return {"id":t.id,"status":t.status}
@router.post("/users/{target_user_id}/reactivate")
def reactivate_user(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 t=db.query(User).filter(User.id==target_user_id).first()
 if not t: raise HTTPException(404,"User not found")
 t.status="active"; db.commit(); log_action(db,"ACCOUNT_REACTIVATED",user_id=user.id,target=t.id); return {"id":t.id,"status":t.status}
@router.get("/users/{target_user_id}/history")
def user_history(target_user_id,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 if not db.query(User).filter(User.id==target_user_id).first(): raise HTTPException(404,"User not found")
 return to_dict_list(db.query(AuditLog).filter(AuditLog.user_id==target_user_id).order_by(AuditLog.created_at.desc()).limit(200).all())
@router.get("/stats")
def stats(user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 return {"total_donors":db.query(DonorProfile).count(),"active_donors":db.query(DonorProfile).filter(DonorProfile.availability_status=="active").count(),"total_recipients":db.query(Patient).count(),"active_cases":db.query(TransplantCase).filter(TransplantCase.stage.notin_(["COMPLETED","CANCELLED","REJECTED"])).count(),"registered_hospitals":db.query(HospitalProfile).count(),"approved_doctors":db.query(DoctorProfile).filter(DoctorProfile.approval_status.in_(["approved","APPROVED"])).count(),"pending_doctors":db.query(DoctorProfile).filter(DoctorProfile.approval_status.in_(["pending","PENDING_APPROVAL","ORGANIZER_REVIEW","REQUESTED_INFO"])).count(),"emergency_requests":db.query(EmergencyRequest).count(),"matching_requests":db.query(MatchRequest).count(),"successful_matches":db.query(MatchResult).filter(MatchResult.overall_score>=80).count(),"completed_transplant_cases":db.query(TransplantCase).filter(TransplantCase.stage=="COMPLETED").count()}
@router.get("/transplant-cases")
def transplant_cases(page:int=1,page_size:int=DEFAULT_PAGE_SIZE,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 page,page_size=bounded_page(page,page_size)
 paginated=paginate(db.query(TransplantCase).order_by(TransplantCase.created_at.desc()),page,page_size)
 return {**paginated,"items":to_dict_list(paginated["items"])}
@router.get("/emergencies")
def emergencies(page:int=1,page_size:int=DEFAULT_PAGE_SIZE,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 page,page_size=bounded_page(page,page_size)
 paginated=paginate(db.query(EmergencyRequest).order_by(EmergencyRequest.created_at.desc()),page,page_size)
 return {**paginated,"items":to_dict_list(paginated["items"])}
@router.get("/matching-requests")
def matching_requests(page:int=1,page_size:int=DEFAULT_PAGE_SIZE,user=Depends(require_role("organizer")),db:Session=Depends(get_db)):
 page,page_size=bounded_page(page,page_size)
 paginated=paginate(db.query(MatchRequest).order_by(MatchRequest.created_at.desc()),page,page_size)
 return {**paginated,"items":to_dict_list(paginated["items"])}
@router.get("/audit-log")
def audit_log(limit:int=100,user=Depends(require_role("organizer")),db:Session=Depends(get_db)): return to_dict_list(db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all())
