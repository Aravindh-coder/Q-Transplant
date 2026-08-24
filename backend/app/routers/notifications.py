from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import decode_token, oauth2_scheme
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.schemas.domain import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications & Alerts"])


def _current_user_id(token: str) -> int:
    payload = decode_token(token)
    return int(payload.get("sub"))


@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = _current_user_id(token)
    repo = AuditRepository(db)
    return repo.get_user_notifications(user_id)


@router.get("/unread-count")
def get_unread_count(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = _current_user_id(token)
    repo = AuditRepository(db)
    return {"unread_count": repo.get_unread_count(user_id)}


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = _current_user_id(token)
    repo = AuditRepository(db)
    notif = repo.mark_as_read(user_id, notification_id)
    if notif is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    return notif


@router.post("/mark-all-read")
def mark_all_notifications_read(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = _current_user_id(token)
    repo = AuditRepository(db)
    updated = repo.mark_all_as_read(user_id)
    return {"marked_read": updated}
