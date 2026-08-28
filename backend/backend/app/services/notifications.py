from sqlalchemy.orm import Session
from app.models import Notification, User
from app.services.mailer import send_email
from app.config import settings


def notify(db: Session, recipient: User, title: str, message: str,
           priority: str = "normal", also_email: bool = False) -> Notification:
    n = Notification(recipient_user_id=recipient.id, type="IN_APP", title=title,
                     message=message, priority=priority)
    db.add(n)
    db.flush()
    if also_email:
        try:
            send_email(recipient.email, title, message)
        except RuntimeError:
            pass
    return n


def notify_role(db: Session, role: str, title: str, message: str,
                priority: str = "normal", also_email: bool = False) -> int:
    users = db.query(User).filter(User.role == role, User.status == "active").all()
    for user in users:
        notify(db, user, title, message, priority, also_email)
    return len(users)


def notify_organizer(title: str, message: str) -> None:
    if not settings.ORGANIZER_EMAIL:
        return
    try:
        send_email(settings.ORGANIZER_EMAIL, title, message)
    except RuntimeError:
        pass
