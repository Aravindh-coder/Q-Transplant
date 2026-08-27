from sqlalchemy.orm import Session
from app.models import AuditLog


def log_action(db: Session, action: str, user_id: str | None = None, target: str | None = None,
                meta: dict | None = None, ip_address: str | None = None) -> AuditLog:
    entry = AuditLog(user_id=user_id, action=action, target=target, meta=meta or {}, ip_address=ip_address)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
