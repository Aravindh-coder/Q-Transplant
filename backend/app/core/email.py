import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.app.core.config import settings
from backend.app.core.logging import logger


class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body_html: str) -> bool:
        """Sends an SMTP email with HTML body. In dev/fallback mode, logs the output cleanly."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email

            part_html = MIMEText(body_html, "html")
            msg.attach(part_html)

            # Check if using default example SMTP host
            if "example.com" in settings.SMTP_HOST:
                logger.info(f"[EMAIL DEV MOCK] To: {to_email} | Subject: {subject}")
                logger.info(f"[EMAIL BODY]:\n{body_html[:300]}...")
                return True

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
            logger.info(f"Email successfully sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            # Log payload for audit
            logger.info(f"[EMAIL FAIL MOCK DELIVERED] To: {to_email} | Subject: {subject}")
            return False

    @classmethod
    def send_registration_ack(cls, email: str, name: str, role: str):
        subject = "Q-Transplant Registration Acknowledgment"
        body = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #161616; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-top: 4px solid #0f62fe; padding: 30px;">
                <h2 style="color: #0f62fe; margin-top: 0;">Q-Transplant Platform</h2>
                <p>Hello <strong>{name}</strong>,</p>
                <p>Thank you for registering on Q-Transplant as a <strong>{role.upper()}</strong>.</p>
                <p>Your account registration has been received and is currently under review by our Organ Transplant Coordination Board.</p>
                <p>You will receive another email once your registration status is approved.</p>
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;" />
                <p style="font-size: 12px; color: #6f6f6f;">Q-Transplant Enterprise Organ Coordination Network</p>
            </div>
        </div>
        """
        return cls.send_email(email, subject, body)

    @classmethod
    def send_approval_status(cls, email: str, name: str, approved: bool, reason: str = ""):
        status_text = "APPROVED" if approved else "REJECTED"
        color = "#198038" if approved else "#da1e28"
        subject = f"Q-Transplant Account Status Update: {status_text}"
        body = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #161616; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-top: 4px solid {color}; padding: 30px;">
                <h2 style="color: {color}; margin-top: 0;">Q-Transplant Account {status_text}</h2>
                <p>Hello <strong>{name}</strong>,</p>
                <p>Your account request has been <strong>{status_text}</strong> by the system administrator.</p>
                {f'<p><strong>Reason / Note:</strong> {reason}</p>' if reason else ''}
                <p>Log in to your portal to access your coordination dashboard.</p>
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;" />
                <p style="font-size: 12px; color: #6f6f6f;">Q-Transplant Security & Compliance</p>
            </div>
        </div>
        """
        return cls.send_email(email, subject, body)

    @classmethod
    def send_match_notification(cls, email: str, recipient_name: str, organ_type: str, match_score: float):
        subject = f"CRITICAL ALERT: Organ Match Found ({organ_type.upper()})"
        body = f"""
        <div style="font-family: Arial, sans-serif; padding: 20px; color: #161616; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-top: 4px solid #da1e28; padding: 30px;">
                <h2 style="color: #da1e28; margin-top: 0;">Organ Compatibility Alert</h2>
                <p>Attention Dr./Coordinator <strong>{recipient_name}</strong>,</p>
                <p>A high-compatibility <strong>{organ_type.upper()}</strong> organ offer has been computed with a compatibility score of <strong>{match_score:.1f}%</strong>.</p>
                <p>Please log in immediately to review medical cross-match metrics and cold-box transport dispatch status.</p>
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;" />
                <p style="font-size: 12px; color: #6f6f6f;">Q-Transplant Emergency Dispatch</p>
            </div>
        </div>
        """
        return cls.send_email(email, subject, body)
