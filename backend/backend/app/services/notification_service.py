"""Central notification dispatcher for Q-Transplant."""
from app.models import Notification
from app.services.notifications import notify

TYPES = {"EMAIL", "IN_APP", "REAL_TIME", "ESP32"}


def create_notification(db, recipient, notification_type, title, message, priority="normal"):
    notification_type = notification_type.upper()
    if notification_type not in TYPES:
        raise ValueError(f"Unsupported notification type: {notification_type}")
    row = Notification(recipient_user_id=recipient.id, type=notification_type,
                       title=title, message=message, priority=priority, read=False)
    db.add(row)
    db.flush()
    return row
