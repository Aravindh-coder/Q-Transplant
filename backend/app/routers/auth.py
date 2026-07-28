from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import (
    get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token, oauth2_scheme
)
from backend.app.core.email import EmailService
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.schemas.auth import UserRegister, UserLogin, Token, RefreshTokenRequest
from backend.app.schemas.domain import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])


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

    # Organizer / Admin accounts are auto-approved; others require review
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

    # Create role specific profile
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
