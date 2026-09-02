from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, TransplantCase, Patient, HospitalProfile, DoctorProfile, DonorProfile
from app.security import require_role, get_current_user
from app.services.audit import log_action
from app.services.case_workflow import validate_transition, STATES
from app.services.notifications import notify, notify_role
from app.services.search_service import paginate
from app.services.performance import bounded_page, DEFAULT_PAGE_SIZE
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/transplants", tags=["transplants"])


def _scope_query(q, user: User, db: Session):
    """Same visibility rule spec section 38 asks for everywhere: a doctor
    only sees their own hospital's cases, a hospital only its own, an
    organizer sees everything (with every access still audited)."""
    if user.role == "doctor":
        doctor = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
        if not doctor or not doctor.hospital_id:
            return q.filter(TransplantCase.id == None)  # no hospital link yet -> nothing visible
        return q.filter(TransplantCase.hospital_id == doctor.hospital_id)
    if user.role == "hospital":
        hospital = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        if not hospital:
            return q.filter(TransplantCase.id == None)
        return q.filter(TransplantCase.hospital_id == hospital.id)
    return q  # organizer: unrestricted, every access still audit-logged


class TransplantCaseIn(BaseModel):
    patient_id: str
    donor_id: Optional[str] = None


class TransitionIn(BaseModel):
    new_stage: str
    note: Optional[str] = None


@router.get("/health")
def transplant_api_health(user: User = Depends(require_role("doctor", "hospital", "organizer"))):
    return {"status": "ready", "message": "Transplant coordination API available"}


@router.get("/stages")
def list_stages():
    """The full case lifecycle this API enforces -- exposed so a frontend
    can render the pipeline without hardcoding it twice."""
    return {"stages": list(STATES)}


@router.post("")
def create_case(body: TransplantCaseIn, user: User = Depends(require_role("doctor", "hospital")), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == body.patient_id).first()
    if not patient:
        raise HTTPException(404, "Patient not found.")
    if user.role == "doctor":
        doctor = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
        if not doctor or doctor.id != patient.doctor_id:
            raise HTTPException(403, "You can only open a transplant case for your own patient.")
    else:
        hospital = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        if not hospital or hospital.id != patient.hospital_id:
            raise HTTPException(403, "You can only open a transplant case for your own hospital's patient.")
    if body.donor_id and not db.query(DonorProfile).filter(DonorProfile.id == body.donor_id).first():
        raise HTTPException(404, "Donor not found.")
    case = TransplantCase(patient_id=patient.id, hospital_id=patient.hospital_id, donor_id=body.donor_id, stage="CREATED")
    db.add(case); db.commit(); db.refresh(case)
    log_action(db, "TRANSPLANT_CASE_CREATED", user_id=user.id, target=case.id, meta={"patient_id": patient.id})
    notify_role(db, "organizer", "New transplant case opened", f"A transplant case was opened for patient {patient.full_name} ({patient.required_organ}).", priority="normal")
    return to_dict(case)


@router.get("")
def list_cases(stage: Optional[str] = None, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
               user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    page, page_size = bounded_page(page, page_size)
    q = _scope_query(db.query(TransplantCase), user, db)
    if stage:
        q = q.filter(TransplantCase.stage == stage.upper())
    paginated = paginate(q.order_by(TransplantCase.created_at.desc()), page, page_size)
    return {**paginated, "items": to_dict_list(paginated["items"])}


@router.get("/{case_id}")
def get_case(case_id: str, user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    case = _scope_query(db.query(TransplantCase).filter(TransplantCase.id == case_id), user, db).first()
    if not case:
        raise HTTPException(404, "Transplant case not found or not accessible.")
    return to_dict(case)


@router.post("/{case_id}/transition")
def transition_case(case_id: str, body: TransitionIn, user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    case = _scope_query(db.query(TransplantCase).filter(TransplantCase.id == case_id), user, db).first()
    if not case:
        raise HTTPException(404, "Transplant case not found or not accessible.")
    try:
        new_stage = validate_transition(case.stage, body.new_stage)
    except ValueError as e:
        raise HTTPException(400, str(e))
    old_stage = case.stage
    case.stage = new_stage
    db.commit()
    log_action(db, "TRANSPLANT_CASE_TRANSITIONED", user_id=user.id, target=case.id, meta={"from": old_stage, "to": new_stage, "note": body.note})
    notify_role(db, "organizer", f"Transplant case moved to {new_stage}",
                f"Case {case.id[:8]} moved from {old_stage} to {new_stage}." + (f" Note: {body.note}" if body.note else ""),
                priority="high" if new_stage in ("APPROVED_FOR_PROCEDURE", "PROCEDURE_SCHEDULED", "COMPLETED") else "normal")
    return to_dict(case)
