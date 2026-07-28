import base64
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import (
    get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token, oauth2_scheme
)
from backend.app.core.email import EmailService
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.models.domain import PasswordReset
from backend.app.schemas.auth import UserRegister, UserLogin, Token, RefreshTokenRequest
from backend.app.schemas.domain import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])

AVATARS_DIR = "backend/uploads/avatars"
CERTIFICATES_DIR = "backend/uploads/certificates"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    audit = AuditRepository(db)

    existing = repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email address already exists."
        )

    is_approved = True if payload.role.lower() == "organizer" else False
    
    hashed_pwd = get_password_hash(payload.password)
    user = repo.create_user(
        email=payload.email,
        password_hash=hashed_pwd,
        full_name=payload.full_name,
        role=payload.role.lower(),
        phone=payload.phone,
        is_approved=is_approved
    )

    if payload.role.lower() == "hospital":
        repo.create_hospital_profile(
            user_id=user.id,
            name=payload.full_name,
            license_number=payload.license_number or f"LIC-{user.id:04d}",
            city=payload.city or "Bengaluru",
            state=payload.state or "Karnataka",
            address=payload.address or "Main Medical Square",
            contact_phone=payload.phone or "080-555-0199"
        )
    elif payload.role.lower() == "doctor":
        repo.create_doctor_profile(
            user_id=user.id,
            medical_license=payload.license_number or f"MED-{user.id:04d}",
            specialization=payload.specialization or "Transplant Surgery",
            department=payload.department or "Cardiothoracic",
            phone=payload.phone or "080-555-0188"
        )
    elif payload.role.lower() == "donor":
        repo.create_donor_profile(
            user_id=user.id,
            blood_type=payload.blood_type or "O+",
            hla_type=payload.hla_type or "A2,B7,DR4",
            age=payload.age or 35,
            gender=payload.gender or "Male"
        )
    elif payload.role.lower() == "patient":
        repo.create_patient_profile(
            user_id=user.id,
            blood_type=payload.blood_type or "O+",
            hla_type=payload.hla_type or "A2,B7,DR4",
            target_organ=payload.target_organ or "Heart",
            urgency_score=8
        )

    audit.log_action(user_id=user.id, action="REGISTER", resource="User", details=f"Registered role {user.role}")
    EmailService.send_registration_ack(user.email, user.full_name, user.role)

    return user


@router.post("/register-doctor-camera", response_model=UserOut, status_code=status.HTTP_201_CREATED)

def register_doctor_camera(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    phone: str = Form(...),
    license_number: str = Form(...),
    specialization: str = Form(...),
    department: str = Form(...),
    camera_image_base64: str = Form(...),
    db: Session = Depends(get_db)
):
    repo = UserRepository(db)
    audit = AuditRepository(db)

    if repo.get_by_email(email):
        raise HTTPException(status_code=400, detail="Doctor email address already registered.")

    # Process and save live camera photo
    filename = f"avatar_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(AVATARS_DIR, filename)

    try:
        header, encoded = camera_image_base64.split(",", 1) if "," in camera_image_base64 else ("", camera_image_base64)
        image_bytes = base64.b64decode(encoded)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        filepath = f"/uploads/avatars/default_doctor.jpg"

    user = repo.create_user(
        email=email,
        password_hash=get_password_hash(password),
        full_name=full_name,
        role="doctor",
        phone=phone,
        is_approved=False  # Requires Admin Approval
    )

    doc = repo.create_doctor_profile(
        user_id=user.id,
        medical_license=license_number,
        specialization=specialization,
        department=department,
        phone=phone
    )
    doc.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()

    audit.log_action(user_id=user.id, action="REGISTER_CAMERA", resource="Doctor", details=f"Saved camera capture: {filename}")
    EmailService.send_registration_ack(user.email, user.full_name, "doctor")
    return user


@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    audit = AuditRepository(db)

    user = repo.get_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support."
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id, role=user.role)

    audit.log_action(user_id=user.id, action="LOGIN", resource="User", details="Successful authentication")

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_approved=user.is_approved
    )


@router.post("/forgot-password")
def request_password_reset(email: str = Form(...), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_email(email)
    if not user:
        # Prevent user enumeration
        return {"message": "If the account exists, a password reset link has been dispatched to your email."}

    reset_token = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

    pwd_reset = PasswordReset(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used=False
    )
    db.add(pwd_reset)
    db.commit()

    reset_link = f"http://localhost:5173/#reset-token={reset_token}"
    body = f"""
    <p>Hello <strong>{user.full_name}</strong>,</p>
    <p>A password reset request was issued for your Q-Transplant account.</p>
    <p>Click the secure link below to set a new password (valid for 15 minutes):</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    """
    EmailService.send_email(user.email, "Q-Transplant Password Reset Link", body)
    return {"message": "Password reset token generated and sent to registered email."}


@router.post("/reset-password")
def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    reset_entry = db.query(PasswordReset).filter(PasswordReset.token == token, PasswordReset.used == False).first()
    if not reset_entry:
        raise HTTPException(status_code=400, detail="Invalid or already used password reset token.")

    if datetime.now(timezone.utc) > reset_entry.expires_at.replace(tzinfo=timezone.utc):
        raise HTTPException(status_code=400, detail="Password reset token has expired.")

    user = db.query(UserRepository(db).get_by_id(reset_entry.user_id))
    user = db.query(PasswordReset).filter(PasswordReset.id == reset_entry.id).first().user
    user.password_hash = get_password_hash(new_password)
    reset_entry.used = True
    db.commit()

    return {"message": "Password successfully updated. You may now log in."}


@router.post("/refresh", response_model=Token)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token type."
        )

    user_id = int(decoded.get("sub"))
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    new_access = create_access_token(subject=user.id, role=user.role)
    new_refresh = create_refresh_token(subject=user.id, role=user.role)

    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_approved=user.is_approved
    )


@router.get("/me", response_model=UserOut)
def get_current_user_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    user_id = int(payload.get("sub"))
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    return user
