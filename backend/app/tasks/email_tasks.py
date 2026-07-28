from backend.app.tasks.celery_app import celery_app
from backend.app.core.email import EmailService


@celery_app.task(name="send_async_email")
def send_async_email_task(to_email: str, subject: str, body_html: str):
    return EmailService.send_email(to_email, subject, body_html)


@celery_app.task(name="send_match_alert_task")
def send_match_alert_task(email: str, name: str, organ_type: str, score: float):
    return EmailService.send_match_notification(email, name, organ_type, score)
