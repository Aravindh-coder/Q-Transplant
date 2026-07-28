import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta, timezone

from backend.app.core.config import settings
from backend.app.core.logging import logger


class EmailService:
    @staticmethod
    def generate_quick_approval_token(user_id: int) -> str:
        payload = {
            "user_id": str(user_id),
            "action": "quick_approve",
            "exp": datetime.now(timezone.utc) + timedelta(days=7)
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def verify_quick_approval_token(token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            if payload.get("action") == "quick_approve":
                return int(payload.get("user_id"))
        except Exception as e:
            logger.warning(f"Invalid quick approval token: {e}")
        return None

    @staticmethod
    def send_email(to_email: str, subject: str, body_html: str) -> bool:
        """Sends an SMTP email with HTML body using TLS or SSL as configured."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email

            part_html = MIMEText(body_html, "html")
            msg.attach(part_html)

            # Fallback mock logger if host is example.com or credentials missing
            if "example.com" in settings.SMTP_HOST or not settings.SMTP_USER:
                logger.info(f"[EMAIL DEV MOCK] To: {to_email} | Subject: {subject}")
                logger.info(f"[EMAIL BODY MOCK SUMMARY]:\n{body_html[:300]}...")
                return True

            if settings.SMTP_PORT == 465:
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    if settings.SMTP_TLS:
                        server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())

            logger.info(f"Email successfully dispatched via SMTP to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to dispatch SMTP email to {to_email}: {str(e)}")
            logger.info(f"[EMAIL FALLBACK LOGGED] To: {to_email} | Subject: {subject}")
            return False

    @classmethod
    def send_registration_ack(cls, email: str, name: str, role: str):
        subject = "Q-Transplant Registration Acknowledgment"
        body = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; padding: 20px; color: #161616; background-color: #161616;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #262626; border-top: 4px solid #0f62fe; padding: 30px; color: #f4f4f4;">
                <h2 style="color: #0f62fe; margin-top: 0;">Q-Transplant Enterprise Platform</h2>
                <p>Hello <strong>{name}</strong>,</p>
                <p>Thank you for registering on Q-Transplant as a <strong>{role.upper()}</strong>.</p>
                <p>Your account request has been logged and is under verification by our Organ Transplant Coordination Board.</p>
                <p>You will receive an automated email as soon as your registration status is reviewed and approved by the system organizer.</p>
                <hr style="border: none; border-top: 1px solid #393939; margin: 20px 0;" />
                <p style="font-size: 12px; color: #c6c6c6;">Q-Transplant Security & Enterprise Governance</p>
            </div>
        </div>
        """
        return cls.send_email(email, subject, body)

    @classmethod
    def send_verification_request_to_organizer(cls, user_id: int, name: str, email: str, spec: str, license_num: str, dept: str, phone: str, avatar_url: Optional[str] = None, base_url: str = "http://localhost:8080"):
        token = cls.generate_quick_approval_token(user_id)
        approve_url = f"{base_url}/api/v1/users/quick-approve?user_id={user_id}&approve=true&token={token}"
        reject_url = f"{base_url}/api/v1/users/quick-approve?user_id={user_id}&approve=false&token={token}"

        photo_html = ""
        if avatar_url:
            if not avatar_url.startswith("http"):
                full_img_url = f"{base_url}{avatar_url}"
            else:
                full_img_url = avatar_url
            photo_html = f"""
            <div style="margin-bottom: 20px; text-align: center;">
                <img src="{full_img_url}" alt="Doctor Photo" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #0f62fe; box-shadow: 0 4px 10px rgba(0,0,0,0.5);" />
                <p style="font-size: 12px; color: #8d8d8d; margin-top: 5px;">Live Verification Snapshot</p>
            </div>
            """

        subject = f"URGENT VERIFICATION REQUEST: Dr. {name} (License: {license_num})"
        body = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; padding: 20px; color: #f4f4f4; background-color: #161616;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #262626; border-top: 4px solid #f1c21b; padding: 30px;">
                <h2 style="color: #f1c21b; margin-top: 0;">Organizer Verification Required</h2>
                <p>A new Doctor registration requires executive approval before granting access to organ matching registries.</p>
                
                {photo_html}

                <div style="background-color: #161616; padding: 15px; border-left: 3px solid #0f62fe; margin-bottom: 20px;">
                    <p style="margin: 4px 0;"><strong>Doctor Name:</strong> Dr. {name}</p>
                    <p style="margin: 4px 0;"><strong>Email Address:</strong> {email}</p>
                    <p style="margin: 4px 0;"><strong>Medical License:</strong> {license_num}</p>
                    <p style="margin: 4px 0;"><strong>Specialization:</strong> {spec}</p>
                    <p style="margin: 4px 0;"><strong>Department:</strong> {dept}</p>
                    <p style="margin: 4px 0;"><strong>Contact Phone:</strong> {phone}</p>
                </div>

                <p style="margin-bottom: 20px; font-weight: bold;">One-Click Executive Action Buttons:</p>
                <div style="display: flex; gap: 15px; margin-bottom: 25px;">
                    <a href="{approve_url}" target="_blank" style="background-color: #24a148; color: #ffffff; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">
                        ✔ APPROVE DOCTOR
                    </a>
                    <a href="{reject_url}" target="_blank" style="background-color: #da1e28; color: #ffffff; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block; margin-left: 10px;">
                        ✖ REJECT REGISTRATION
                    </a>
                </div>

                <hr style="border: none; border-top: 1px solid #393939; margin: 20px 0;" />
                <p style="font-size: 12px; color: #8d8d8d;">Q-Transplant Administrator Automated Verification System</p>
            </div>
        </div>
        """
        organizer_email = settings.ORGANIZER_EMAIL
        return cls.send_email(organizer_email, subject, body)

    @classmethod
    def send_approval_status(cls, email: str, name: str, approved: bool, reason: str = ""):
        status_text = "APPROVED" if approved else "REJECTED"
        color = "#24a148" if approved else "#da1e28"
        subject = f"Q-Transplant Account Status Update: {status_text}"
        body = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; padding: 20px; color: #f4f4f4; background-color: #161616;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #262626; border-top: 4px solid {color}; padding: 30px;">
                <h2 style="color: {color}; margin-top: 0;">Account Registration {status_text}</h2>
                <p>Hello <strong>{name}</strong>,</p>
                <p>Your registration request has been officially <strong>{status_text}</strong> by the Transplant Coordination Board.</p>
                {f'<p style="background:#161616; padding:10px; border-left: 3px solid {color};"><strong>Note:</strong> {reason}</p>' if reason else ''}
                {f'<p><a href="http://localhost:5173" style="background:#0f62fe; color:#fff; padding:10px 20px; text-decoration:none; display:inline-block; margin-top:10px;">Log In to Portal</a></p>' if approved else ''}
                <hr style="border: none; border-top: 1px solid #393939; margin: 20px 0;" />
                <p style="font-size: 12px; color: #8d8d8d;">Q-Transplant Security & Compliance</p>
            </div>
        </div>
        """
        return cls.send_email(email, subject, body)

    @classmethod
    def send_match_notification(cls, email: str, recipient_name: str, organ_type: str, match_score: float):
        subject = f"CRITICAL ALERT: Organ Match Found ({organ_type.upper()})"
        body = f"""
        <div style="font-family: 'Helvetica Neue', Arial, sans-serif; padding: 20px; color: #f4f4f4; background-color: #161616;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #262626; border-top: 4px solid #da1e28; padding: 30px;">
                <h2 style="color: #da1e28; margin-top: 0;">Organ Compatibility Alert</h2>
                <p>Attention Dr./Coordinator <strong>{recipient_name}</strong>,</p>
                <p>A high-compatibility <strong>{organ_type.upper()}</strong> organ offer has been computed with a compatibility score of <strong>{match_score:.1f}%</strong>.</p>
                <p>Please log in immediately to review cross-match metrics and cold-box transport dispatch status.</p>
                <hr style="border: none; border-top: 1px solid #393939; margin: 20px 0;" />
                <p style="font-size: 12px; color: #8d8d8d;">Q-Transplant Emergency Dispatch</p>
            </div>
        </div>
        """
        return cls.send_email(email, subject, body)
