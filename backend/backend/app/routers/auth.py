import random
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, OTP, DoctorProfile, HospitalProfile, DonorProfile
from app.security import hash_password, verify_password, create_access_token, get_current_user, rate_limit
from app.services.mailer import send_email
from app.services.audit import log_action

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: str
    full_name: Optional[str] = None
    license_number: Optional[str] = None
    specialty: Optional[str] = None
    hospital_id: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_code: Optional[str] = None
    blood_group: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailIn(BaseModel):
    email: EmailStr
    otp: str


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


def _send_verification(user: User, db: Session) -> None:
    code = f"{random.randint(0, 999999):06d}"
    db.add(OTP(email=user.email, code_hash=hash_password(code), purpose="email_verify",
               expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)))
    db.commit()
    try:
        send_email(user.email, "Q-Transplant — verify your email",
                   f"Your Q-Transplant verification code is {code}. It expires in "
                   f"{settings.OTP_EXPIRY_MINUTES} minutes. Do not share this code.")
    except RuntimeError:
        # Account remains unverified; the UI can use resend after SMTP is configured.
        pass


@router.post("/register")
def register(body: RegisterIn, request: Request, db: Session = Depends(get_db)):
    if body.role == "organizer":
        raise HTTPException(400, "Organizer accounts are provisioned via environment variables, not self-registration.")
    if body.role not in ("donor", "doctor", "hospital"):
        raise HTTPException(400, "role must be one of: donor, doctor, hospital")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, "An account with this email already exists.")
    if body.role == "doctor" and not body.license_number:
        raise HTTPException(400, "license_number is required to register as a doctor.")
    if body.role == "hospital" and not (body.hospital_name and body.hospital_code):
        raise HTTPException(400, "hospital_name and hospital_code are required to register as a hospital.")
    if body.role == "donor" and not body.blood_group:
        raise HTTPException(400, "blood_group is required to register as a donor.")

    # Donors must verify email before they can log in. Doctors retain their existing
    # organizer-approval gate; hospitals retain pending verification behavior.
    status_value = "unverified" if body.role == "donor" else ("pending" if body.role == "doctor" else "active")
    user = User(email=body.email, hashed_password=hash_password(body.password), role=body.role,
                full_name=body.full_name, status=status_value, email_verified=False)
    db.add(user)
    db.commit()
    db.refresh(user)

    if body.role == "doctor":
        db.add(DoctorProfile(user_id=user.id, license_number=body.license_number,
                              specialty=body.specialty, hospital_id=body.hospital_id,
                              approval_status="pending"))
    elif body.role == "hospital":
        db.add(HospitalProfile(user_id=user.id, hospital_name=body.hospital_name,
                               hospital_code=body.hospital_code, verification_status="pending"))
    else:
        db.add(DonorProfile(user_id=user.id, blood_group=body.blood_group.upper(), donation_status="ACTIVE"))
    db.commit()
    log_action(db, "REGISTER", user_id=user.id, target=body.role.upper(),
               ip_address=request.client.host if request.client else None)

    if body.role == "donor":
        _send_verification(user, db)
    elif body.role == "doctor":
        try:
            send_email(body.email, "Q-Transplant — registration received",
                       "Your doctor account is pending organizer approval.")
            send_email(settings.ORGANIZER_EMAIL, "Q-Transplant — new doctor pending approval",
                       f"{body.full_name or body.email} registered as a doctor (license {body.license_number}).")
        except RuntimeError:
            pass

    return {"id": user.id, "status": user.status, "email_verification_required": body.role == "donor"}


@router.post("/verify-email", dependencies=[Depends(rate_limit("otp", settings.OTP_RATE_LIMIT, settings.RATE_LIMIT_WINDOW_MINUTES))])
def verify_email(body: VerifyEmailIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(404, "Account not found.")
    if user.email_verified:
        return {"message": "Email already verified."}
    otp_row = (db.query(OTP)
               .filter(OTP.email == body.email, OTP.used == False, OTP.purpose == "email_verify")  # noqa: E712
               .order_by(OTP.created_at.desc()).first())
    if not otp_row or otp_row.expires_at < datetime.now(timezone.utc) or not verify_password(body.otp, otp_row.code_hash):
        raise HTTPException(400, "Invalid or expired verification OTP.")
    otp_row.used = True
    user.email_verified = True
    if user.role == "donor" and user.status == "unverified":
        user.status = "active"
    db.commit()
    log_action(db, "EMAIL_VERIFIED", user_id=user.id)
    return {"message": "Email verified successfully. You can now log in.", "status": user.status}


@router.post("/resend-verification", dependencies=[Depends(rate_limit("otp", settings.OTP_RATE_LIMIT, settings.RATE_LIMIT_WINDOW_MINUTES))])
def resend_verification(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if user and not user.email_verified:
        _send_verification(user, db)
    return {"message": "If the account exists and is unverified, a verification OTP has been sent."}


@router.post("/login", dependencies=[Depends(rate_limit("login", settings.LOGIN_RATE_LIMIT, settings.RATE_LIMIT_WINDOW_MINUTES))])
def login(body: LoginIn, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password.")
    if user.status == "suspended":
        raise HTTPException(403, "This account has been suspended.")
    if user.role == "donor" and not user.email_verified:
        raise HTTPException(403, "Verify your email with the 6-digit OTP before logging in.")
    if user.status == "pending":
        raise HTTPException(403, "This account is still pending organizer approval.")
    log_action(db, "LOGIN", user_id=user.id, ip_address=request.client.host if request.client else None)
    return {"access_token": create_access_token(user), "token_type": "bearer", "role": user.role, "user_id": user.id}


@router.post("/forgot-password", dependencies=[Depends(rate_limit("otp", settings.OTP_RATE_LIMIT, settings.RATE_LIMIT_WINDOW_MINUTES))])
def forgot_password(body: ForgotPasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        code = f"{random.randint(0, 999999):06d}"
        db.add(OTP(email=body.email, code_hash=hash_password(code), purpose="password_reset",
                   expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)))
        db.commit()
        try:
            send_email(body.email, "Q-Transplant — your password reset code",
                       f"Your one-time code is {code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes.")
        except RuntimeError:
            pass
        log_action(db, "OTP_REQUESTED", user_id=user.id)
    return {"message": "If that email is registered, an OTP has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordIn, db: Session = Depends(get_db)):
    otp_row = (db.query(OTP).filter(OTP.email == body.email, OTP.used == False,
               OTP.purpose == "password_reset").order_by(OTP.expires_at.desc()).first())  # noqa: E712
    if not otp_row or otp_row.expires_at < datetime.now(timezone.utc) or not verify_password(body.otp, otp_row.code_hash):
        raise HTTPException(400, "Invalid or expired OTP.")
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(404, "Account not found.")
    user.hashed_password = hash_password(body.new_password)
    otp_row.used = True
    db.commit()
    log_action(db, "PASSWORD_RESET", user_id=user.id, target="via OTP")
    return {"message": "Password updated. You can log in with your new password."}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role, "status": user.status,
            "email_verified": user.email_verified}
