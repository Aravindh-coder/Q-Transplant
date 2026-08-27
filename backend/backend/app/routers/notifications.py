from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Notification
from app.security import get_current_user
from app.utils import to_dict_list

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/me")
def my_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (db.query(Notification)
            .filter(Notification.recipient_user_id == user.id)
            .order_by(Notification.created_at.desc()).limit(100).all())
    return to_dict_list(rows)


@router.post("/{notification_id}/read")
def mark_read(notification_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = (db.query(Notification)
           .filter(Notification.id == notification_id, Notification.recipient_user_id == user.id).first())
    if not row:
        return {"ok": True}
    row.read = True
    db.commit()
    return {"id": row.id, "read": True}
