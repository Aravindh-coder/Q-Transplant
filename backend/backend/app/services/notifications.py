from sqlalchemy.orm import Session
from app.models import Notification, User
from app.services.mailer import send_email


def notify(db: Session, recipient: User, title: str, message: str,
           priority: str = "normal", also_email: bool = False) -> Notification:
    n = Notification(recipient_user_id=recipient.id, type="IN_APP", title=title,
                      message=message, priority=priority)
    db.add(n)
    db.commit()
    db.refresh(n)

    if also_email:
        try:
            send_email(recipient.email, title, message)
        except RuntimeError:
            # email not configured in this environment (e.g. local dev) —
            # the in-app notification still exists, so nothing is silently lost.
            pass
    return n
