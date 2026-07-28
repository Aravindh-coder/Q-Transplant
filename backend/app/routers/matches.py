from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
from backend.app.core.email import EmailService
from backend.app.repositories.organ_repo import OrganRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.services.quantum_matching import QuantumMatchingEngine
from backend.app.schemas.domain import MatchOut

router = APIRouter(prefix="/matches", tags=["Quantum-Inspired Matching & Allocation Engine"])


@router.post("/compute/{organ_id}", response_model=List[MatchOut])
def compute_quantum_organ_matches(
    organ_id: int,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer", "doctor"]))
):
    organ_repo = OrganRepository(db)
    user_repo = UserRepository(db)
    audit = AuditRepository(db)

    organ = organ_repo.get_organ_by_id(organ_id)
    if not organ:
        raise HTTPException(status_code=404, detail="Organ not found.")

    patients = organ_repo.list_all_patients()
    created_matches = []

    for patient in patients:
        # Run Quantum-Inspired Multi-Factor Optimization
        quantum_res = QuantumMatchingEngine.compute_quantum_match(organ, patient, distance_km=18.5, icu_capacity_percent=85.0)
        score = quantum_res["confidence_score"]

        if quantum_res["is_viable"]:
            match = organ_repo.create_match(
                organ_id=organ.id,
                patient_id=patient.id,
                compatibility_score=score,
                distance_km=18.5
            )
            match.match_rationale = quantum_res["rationale"]
            db.commit()
            db.refresh(match)
            created_matches.append(match)

            patient_user = user_repo.get_by_id(patient.user_id)
            if patient_user:
                EmailService.send_match_notification(
                    email=patient_user.email,
                    recipient_name=patient_user.full_name,
                    organ_type=organ.organ_type,
                    match_score=score
                )

    user_id = int(current_token.get("sub"))
    audit.log_action(
        user_id=user_id,
        action="QUANTUM_MATCH_COMPUTE",
        resource="Match",
        details=f"Computed {len(created_matches)} quantum candidates for organ {organ.organ_type} (ID: {organ.id})"
    )

    return created_matches


@router.get("/", response_model=List[MatchOut])
def list_matches(db: Session = Depends(get_db)):
    repo = OrganRepository(db)
    return repo.list_matches()


@router.post("/{match_id}/approve", response_model=MatchOut)
def approve_transplant_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer", "doctor"]))
):
    repo = OrganRepository(db)
    audit = AuditRepository(db)

    match = repo.update_match_status(match_id, "approved")
    if not match:
        raise HTTPException(status_code=404, detail="Match record not found.")

    user_id = int(current_token.get("sub"))
    audit.log_action(
        user_id=user_id,
        action="APPROVE_MATCH",
        resource="Match",
        details=f"Approved transplant match ID {match_id}"
    )

    return match
