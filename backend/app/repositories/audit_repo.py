from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.domain import AuditLog, Notification


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        user_id: Optional[int],
        action: str,
        resource: str,
        details: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs(self, limit: int = 100) -> List[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()

    def create_notification(self, user_id: int, title: str, message: str, notification_type: str = "info") -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif

    def get_user_notifications(self, user_id: int) -> List[Notification]:
        return self.db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
