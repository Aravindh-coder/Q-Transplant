from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, DonorProfile, Patient, DoctorProfile, HospitalProfile
from app.security import require_role
from app.services.hla import calculate_hla_match
from app.services.audit import log_action

router = APIRouter(prefix="/api/v1/hla", tags=["hla"])


@router.get("/health")
def hla_health(user: User = Depends(require_role("doctor", "hospital", "organizer"))):
    return {"status": "ready", "supported_markers": ["HLA-A", "HLA-B", "HLA-C", "HLA-DR", "HLA-DQ"]}


class HLAProfileIn(BaseModel):
    hla_a: Optional[str] = None
    hla_b: Optional[str] = None
    hla_c: Optional[str] = None
    hla_dr: Optional[str] = None
    hla_dq: Optional[str] = None


class HLACompareIn(BaseModel):
    donor: HLAProfileIn
    recipient: HLAProfileIn


@router.post("/compare")
def compare_hla(body: HLACompareIn, user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    """Standalone HLA comparison -- enter two typing profiles directly. Not
    a data-exposure concern in itself: the caller already has both profiles
    (they typed them in), this just runs the same deterministic scoring the
    live matching engine uses so 'what would this compatibility look like'
    gets a real answer instead of a guess."""
    result = calculate_hla_match(body.donor.model_dump(), body.recipient.model_dump())
    log_action(db, "HLA_COMPARE_AD_HOC", user_id=user.id, meta={"score": result.get("score")})
    return result


@router.post("/compare/{donor_id}/{patient_id}")
def compare_hla_by_id(donor_id: str, patient_id: str, user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    """Raw allele-level detail for a specific donor/patient pair, by their
    saved record IDs. This is the restricted drill-down: routine match
    results only ever show an HLA *score*, never both parties' raw typing
    (see evaluate_candidate's include_hla_detail docs) -- a doctor or
    hospital reviewing a specific candidate calls this deliberately, and
    only for a patient their own hospital actually owns. Organizer is
    unrestricted, with the access itself always audit-logged as the
    compensating control (spec: 'sensitive-record access' must be logged)."""
    donor = db.query(DonorProfile).filter(DonorProfile.id == donor_id).first()
    if not donor:
        raise HTTPException(404, "Donor not found.")
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "Patient not found.")
    if user.role == "doctor":
        doctor = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
        if not doctor or doctor.hospital_id != patient.hospital_id:
            raise HTTPException(403, "You are not authorized to view HLA detail for this patient.")
    elif user.role == "hospital":
        hospital = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        if not hospital or hospital.id != patient.hospital_id:
            raise HTTPException(403, "You are not authorized to view HLA detail for this patient.")
    donor_hla = {"hla_a": donor.hla_a, "hla_b": donor.hla_b, "hla_c": donor.hla_c, "hla_dr": donor.hla_dr, "hla_dq": donor.hla_dq}
    patient_hla = {"hla_a": patient.hla_a, "hla_b": patient.hla_b, "hla_c": patient.hla_c, "hla_dr": patient.hla_dr, "hla_dq": patient.hla_dq}
    result = calculate_hla_match(donor_hla, patient_hla)
    log_action(db, "SENSITIVE_HLA_DETAIL_ACCESSED", user_id=user.id, meta={"donor_id": donor_id, "patient_id": patient_id, "score": result.get("score")})
    return result
