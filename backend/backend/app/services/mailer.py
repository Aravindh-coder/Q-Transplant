"""
Sends every system email from the organizer's Gmail account.
Requires a Gmail App Password (Google Account -> Security -> App passwords),
never the normal account password. Fails loudly if not configured, rather
than silently pretending an email was sent.
"""
import smtplib
import ssl
from email.mime.text import MIMEText

from app.config import settings


def send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.ORGANIZER_APP_PASSWORD:
        raise RuntimeError(
            "ORGANIZER_APP_PASSWORD is not set — cannot send email. "
            "Set it in your environment to enable real email delivery."
        )
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.ORGANIZER_EMAIL
    msg["To"] = to_email
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls(context=context)
        server.login(settings.ORGANIZER_EMAIL, settings.ORGANIZER_APP_PASSWORD)
        server.sendmail(settings.ORGANIZER_EMAIL, [to_email], msg.as_string())
