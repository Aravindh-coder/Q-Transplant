from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import RoleChecker
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.schemas.domain import AuditLogOut

router = APIRouter(prefix="/audit", tags=["Compliance & Audit Logs"])


@router.get("/logs", response_model=List[AuditLogOut])
def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_token: dict = Depends(RoleChecker(["organizer"]))
):
    repo = AuditRepository(db)
    return repo.list_logs(limit=limit)
