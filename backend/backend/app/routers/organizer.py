from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DoctorProfile, DonorProfile, HospitalProfile, Patient, TransplantCase, AuditLog
from app.security import require_role
from app.services.audit import log_action
from app.services.notifications import notify
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/organizer", tags=["organizer"])


@router.get("/doctors/pending")
def pending_doctors(user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    return to_dict_list(db.query(DoctorProfile).filter(DoctorProfile.approval_status == "pending").all())


@router.post("/doctors/{doctor_id}/approve")
def approve_doctor(doctor_id: str, user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if not doctor:
        raise HTTPException(404, "Doctor profile not found.")
    doctor.approval_status = "approved"
    account = db.query(User).filter(User.id == doctor.user_id).first()
    account.status = "active"
    db.commit()

    notify(db, account, "Q-Transplant — you're approved",
           "Your doctor account has been approved. You can now log in and use the doctor portal.",
           priority="high", also_email=True)
    log_action(db, "DOCTOR_APPROVED", user_id=user.id, target=doctor_id)
    return {"id": doctor.id, "approval_status": doctor.approval_status}


@router.post("/doctors/{doctor_id}/reject")
def reject_doctor(doctor_id: str, reason: str = "", user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    doctor = db.query(DoctorProfile).filter(DoctorProfile.id == doctor_id).first()
    if not doctor:
        raise HTTPException(404, "Doctor profile not found.")
    doctor.approval_status = "rejected"
    account = db.query(User).filter(User.id == doctor.user_id).first()
    db.commit()

    notify(db, account, "Q-Transplant — registration update",
           f"Your doctor registration was not approved.{(' Reason: ' + reason) if reason else ''} "
           f"Contact the organizer if you believe this is a mistake.",
           priority="high", also_email=True)
    log_action(db, "DOCTOR_REJECTED", user_id=user.id, target=doctor_id, meta={"reason": reason})
    return {"id": doctor.id, "approval_status": doctor.approval_status}


@router.post("/hospitals/{hospital_id}/verify")
def verify_hospital(hospital_id: str, user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    hospital = db.query(HospitalProfile).filter(HospitalProfile.id == hospital_id).first()
    if not hospital:
        raise HTTPException(404, "Hospital not found.")
    hospital.verification_status = "verified"
    db.commit()
    log_action(db, "HOSPITAL_VERIFIED", user_id=user.id, target=hospital_id)
    return {"id": hospital.id, "verification_status": hospital.verification_status}


@router.post("/users/{target_user_id}/suspend")
def suspend_user(target_user_id: str, user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == target_user_id).first()
    if not target:
        raise HTTPException(404, "User not found.")
    target.status = "suspended"
    db.commit()
    log_action(db, "ACCOUNT_SUSPENDED", user_id=user.id, target=target_user_id)
    return {"id": target.id, "status": target.status}


@router.post("/users/{target_user_id}/reactivate")
def reactivate_user(target_user_id: str, user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == target_user_id).first()
    if not target:
        raise HTTPException(404, "User not found.")
    target.status = "active"
    db.commit()
    log_action(db, "ACCOUNT_REACTIVATED", user_id=user.id, target=target_user_id)
    return {"id": target.id, "status": target.status}


@router.get("/stats")
def stats(user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    return {
        "total_donors": db.query(DonorProfile).count(),
        "active_donors": db.query(DonorProfile).filter(DonorProfile.availability_status == "active").count(),
        "total_recipients": db.query(Patient).count(),
        "active_cases": db.query(TransplantCase).filter(TransplantCase.stage.notin_(["COMPLETED", "CANCELLED", "REJECTED"])).count(),
        "completed_cases": db.query(TransplantCase).filter(TransplantCase.stage == "COMPLETED").count(),
        "registered_hospitals": db.query(HospitalProfile).count(),
        "approved_doctors": db.query(DoctorProfile).filter(DoctorProfile.approval_status == "approved").count(),
        "pending_doctors": db.query(DoctorProfile).filter(DoctorProfile.approval_status == "pending").count(),
    }


@router.get("/audit-log")
def audit_log(limit: int = 100, user: User = Depends(require_role("organizer")), db: Session = Depends(get_db)):
    return to_dict_list(db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all())
