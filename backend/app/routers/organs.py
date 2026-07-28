from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
from backend.app.repositories.organ_repo import OrganRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.schemas.domain import OrganCreate, OrganOut

router = APIRouter(prefix="/organs", tags=["Organ Donation Registry"])


@router.post("/", response_model=OrganOut, status_code=status.HTTP_201_CREATED)
def register_donated_organ(
    payload: OrganCreate,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer", "doctor", "hospital"]))
):
    repo = OrganRepository(db)
    audit = AuditRepository(db)

    organ = repo.create_organ(
        donor_id=payload.donor_id,
        organ_type=payload.organ_type,
        blood_type=payload.blood_type,
        hla_type=payload.hla_type,
        max_ischemia_hours=payload.max_ischemia_hours,
        cold_box_id=payload.cold_box_id
    )

    user_id = int(current_token.get("sub"))
    audit.log_action(
        user_id=user_id,
        action="REGISTER_ORGAN",
        resource="Organ",
        details=f"Registered {payload.organ_type} ({payload.blood_type}) cold_box={payload.cold_box_id}"
    )

    return organ


@router.get("/", response_model=List[OrganOut])
def list_organs(db: Session = Depends(get_db)):
    repo = OrganRepository(db)
    return repo.list_available_organs()


@router.get("/{organ_id}", response_model=OrganOut)
def get_organ(organ_id: int, db: Session = Depends(get_db)):
    repo = OrganRepository(db)
    organ = repo.get_organ_by_id(organ_id)
    if not organ:
        raise HTTPException(status_code=404, detail="Organ record not found.")
    return organ
