from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import decode_token, oauth2_scheme
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.schemas.domain import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications & Alerts"])


@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    repo = AuditRepository(db)
    return repo.get_user_notifications(user_id)
