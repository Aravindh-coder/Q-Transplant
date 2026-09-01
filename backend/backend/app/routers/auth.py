import random
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, OTP, RevokedToken, DoctorProfile, HospitalProfile, DonorProfile
from app.security import hash_password, verify_password, create_access_token, get_current_user, rate_limit, token_fingerprint
from app.services.mailer import send_email
from app.services.audit import log_action
from app.services.observability import safe_event

def _is_expired(expires_at: datetime) -> bool:
    """DateTime columns round-trip as naive on SQLite (and depending on
    driver, elsewhere too) even though everything is written as UTC-aware.
    Comparing that directly against datetime.now(timezone.utc) raises
    TypeError instead of just being wrong -- treat a naive value as UTC."""
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at < datetime.now(timezone.utc)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
class RegisterIn(BaseModel):
    email: EmailStr; password: str = Field(min_length=8); role: str; full_name: str
    phone: Optional[str]=None; address: Optional[str]=None; license_number: Optional[str]=None
    specialty: Optional[str]=None; professional_information: Optional[str]=None; hospital_id: Optional[str]=None
    hospital_name: Optional[str]=None; hospital_code: Optional[str]=None; location: Optional[str]=None
    registration_number: Optional[str]=None; authorized_contact: Optional[str]=None; blood_group: Optional[str]=None
class LoginIn(BaseModel): email: EmailStr; password: str
class VerifyEmailIn(BaseModel): email: EmailStr; otp: str = Field(min_length=6,max_length=6,pattern=r"^\d{6}$")
class ForgotPasswordIn(BaseModel): email: EmailStr
class ResetPasswordIn(BaseModel): email: EmailStr; otp: str = Field(min_length=6,max_length=6,pattern=r"^\d{6}$"); new_password: str = Field(min_length=8)

def _invalidate_otps(db, email, purpose):
    db.query(OTP).filter(OTP.email==email, OTP.purpose==purpose, OTP.used==False).update({OTP.used:True}, synchronize_session=False)

def _issue_otp(db, email, purpose):
    _invalidate_otps(db,email,purpose)
    code=f"{random.SystemRandom().randrange(1000000):06d}"
    row=OTP(email=email,code_hash=hash_password(code),purpose=purpose,expires_at=datetime.now(timezone.utc)+timedelta(minutes=settings.OTP_EXPIRY_MINUTES))
    db.add(row); db.commit(); return code

def _send_verification(user, db):
    code=_issue_otp(db,user.email,"email_verify")
    send_email(user.email,"Q-Transplant — verify your email",f"Your Q-Transplant verification code is {code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes. Do not share this code.")

@router.post("/register")
def register(body:RegisterIn,request:Request,db:Session=Depends(get_db)):
    if body.role=="organizer": raise HTTPException(400,"Organizer accounts can't self-register. The first organizer login is created automatically from the ORGANIZER_BOOTSTRAP_EMAIL / ORGANIZER_BOOTSTRAP_PASSWORD environment variables on startup.")
    if body.role not in ("donor","doctor","hospital"): raise HTTPException(400,"role must be donor, doctor, or hospital")
    existing=db.query(User).filter(User.email==body.email).first()
    if existing:
        # A request can succeed on the server even after the client gives up
        # waiting (a cold Render instance is exactly this scenario) -- if
        # this is genuinely the same person retrying a registration that
        # never got resolved, resume it instead of dead-ending them on a
        # confusing 'already exists' error. Only resumes when the role
        # matches, nothing has been approved/rejected/verified yet, and the
        # password matches (otherwise this is someone else's account and
        # the normal block below is exactly right).
        still_pending = existing.status in ("pending","unverified")
        if existing.role==body.role and still_pending and verify_password(body.password,existing.hashed_password):
            user=existing
            safe_event("register_resumed",user_id=user.id,role=user.role)
        else:
            raise HTTPException(409,"An account with this email already exists.")
    else:
        user=None
    if not body.full_name.strip(): raise HTTPException(400,"full_name is required")
    if body.role=="donor" and (not body.blood_group or not body.phone or not body.address): raise HTTPException(400,"Donor registration requires blood_group, phone and address.")
    if body.role=="doctor" and (not body.phone or not body.address or not body.license_number or not body.specialty or not body.professional_information): raise HTTPException(400,"Doctor registration requires phone, address, license_number, specialty and professional_information. Profile photo and medical certificate must be uploaded before approval.")
    if body.role=="hospital" and (not body.hospital_name or not body.hospital_code or not body.phone or not body.address or not body.location or not body.registration_number or not body.authorized_contact): raise HTTPException(400,"Hospital registration requires all institutional fields.")
    if user is None:
        status="unverified" if body.role=="donor" else "pending"
        user=User(email=body.email,hashed_password=hash_password(body.password),role=body.role,full_name=body.full_name.strip(),status=status,email_verified=False)
        db.add(user); db.commit(); db.refresh(user)
        if body.role=="doctor": db.add(DoctorProfile(user_id=user.id,license_number=body.license_number,phone=body.phone,address=body.address,specialty=body.specialty,professional_information=body.professional_information,hospital_id=body.hospital_id,approval_status="PENDING_APPROVAL"))
        elif body.role=="hospital": db.add(HospitalProfile(user_id=user.id,hospital_name=body.hospital_name,hospital_code=body.hospital_code,phone=body.phone,address=body.address,location=body.location,registration_number=body.registration_number,authorized_contact=body.authorized_contact,verification_status="pending"))
        else: db.add(DonorProfile(user_id=user.id,blood_group=body.blood_group.upper(),phone=body.phone,address=body.address,donation_status="ACTIVE"))
        db.commit(); log_action(db,"REGISTER",user_id=user.id,target=body.role.upper(),ip_address=request.client.host if request.client else None)
        try:
            if body.role=="donor": _send_verification(user,db)
            elif body.role=="doctor":
                send_email(body.email,"Q-Transplant — registration received","Your doctor registration was received and is pending organizer review. Complete the mandatory profile photo and medical certificate upload before approval.")
                if settings.ORGANIZER_EMAIL: send_email(settings.ORGANIZER_EMAIL,"Q-Transplant — new doctor pending approval",f"{body.full_name} registered as a doctor. License: {body.license_number}. Review the submitted registration.")
            elif body.role=="hospital" and settings.ORGANIZER_EMAIL: send_email(body.email,"Q-Transplant — registration received","Your hospital registration was received and is pending verification.")
        except RuntimeError:
            pass
    elif body.role=="donor":
        # Resuming a still-unverified donor registration -- the original
        # OTP may have expired by now, so send a fresh one rather than
        # leaving them stuck with no way to actually verify.
        try: _send_verification(user,db)
        except RuntimeError: pass
    response={"id":user.id,"status":user.status,"email_verification_required":body.role=="donor","approval_required":body.role in ("doctor","hospital")}
    if body.role in ("doctor","hospital"):
        # Normal /login is blocked until organizer approval, but the doctor
        # still needs to submit their photo/certificate (and a hospital its
        # license) for the organizer to review in the first place. This
        # token is scoped by its short expiry, not by role — it works
        # exactly like a normal token for this account, just for 30 minutes.
        response["upload_token"]=create_access_token(user,minutes=30)
    return response

class ResumeRegistrationIn(BaseModel): email: EmailStr; password: str

@router.post("/resume-registration",dependencies=[Depends(rate_limit("resume_registration",settings.LOGIN_RATE_LIMIT,settings.RATE_LIMIT_WINDOW_MINUTES))])
def resume_registration(body:ResumeRegistrationIn,db:Session=Depends(get_db)):
    """If a registration request succeeded on the server but the client
    never got the response (very plausible on a slow cold start), the
    email now shows as 'already exists' with no way back in — the person
    never received their OTP/upload_token and can't re-register with the
    same email. This picks that account back up: same email+password
    proves it's genuinely them, and if the account hasn't been
    approved/verified/rejected yet, this re-issues exactly what the
    original registration response would have given them, so they can
    continue right where they left off instead of being stuck."""
    user=db.query(User).filter(User.email==body.email).first()
    if not user or not verify_password(body.password,user.hashed_password):
        raise HTTPException(401,"Incorrect email or password.")
    if user.role=="organizer": raise HTTPException(400,"Organizer accounts don't go through this flow.")
    if user.email_verified and user.role=="donor": raise HTTPException(400,"This account is already verified — log in normally.")
    if user.role=="doctor":
        d=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
        if d and d.approval_status=="APPROVED": raise HTTPException(400,"This doctor account is already approved — log in normally.")
        if d and d.approval_status=="REJECTED": raise HTTPException(400,"This registration was rejected. Contact the organizer, or register again with different details.")
    if user.role=="hospital":
        h=db.query(HospitalProfile).filter(HospitalProfile.user_id==user.id).first()
        if h and h.verification_status=="verified": raise HTTPException(400,"This hospital account is already verified — log in normally.")
    log_action(db,"REGISTRATION_RESUMED",user_id=user.id,target=user.role.upper())
    if user.role=="donor":
        try: _send_verification(user,db)
        except RuntimeError: pass
        return {"id":user.id,"status":user.status,"email_verification_required":True,"message":"A new verification code has been sent to your email."}
    return {"id":user.id,"status":user.status,"approval_required":True,"upload_token":create_access_token(user,minutes=30),
            "message":"Continue by uploading your documents — your original registration was already received."}

@router.post("/verify-email",dependencies=[Depends(rate_limit("otp_verify",settings.OTP_RATE_LIMIT,settings.RATE_LIMIT_WINDOW_MINUTES))])
def verify_email(body:VerifyEmailIn,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==body.email).first()
    row=db.query(OTP).filter(OTP.email==body.email,OTP.used==False,OTP.purpose=="email_verify").order_by(OTP.created_at.desc()).first()
    if not user or not row or _is_expired(row.expires_at) or not verify_password(body.otp,row.code_hash): raise HTTPException(400,"Invalid or expired verification OTP.")
    row.used=True; user.email_verified=True
    if user.role=="donor": user.status="active"
    db.commit(); log_action(db,"EMAIL_VERIFIED",user_id=user.id); return {"message":"Email verified successfully.","status":user.status}

@router.post("/resend-verification",dependencies=[Depends(rate_limit("otp_resend",settings.OTP_RATE_LIMIT,settings.RATE_LIMIT_WINDOW_MINUTES))])
def resend_verification(body:ForgotPasswordIn,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==body.email).first()
    if user and not user.email_verified:
        try: _send_verification(user,db)
        except RuntimeError: pass
    return {"message":"If the account exists and is unverified, a verification OTP has been sent."}

@router.post("/login",dependencies=[Depends(rate_limit("login",settings.LOGIN_RATE_LIMIT,settings.RATE_LIMIT_WINDOW_MINUTES))])
def login(body:LoginIn,request:Request,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==body.email).first()
    if not user or not verify_password(body.password,user.hashed_password):
        safe_event("login_failed",email=body.email,reason="invalid_credentials")
        raise HTTPException(401,"Incorrect email or password.")
    if user.status in ("suspended","inactive"): raise HTTPException(403,"This account is not active.")
    if not user.email_verified: raise HTTPException(403,"Verify your email before logging in.")
    if user.role=="doctor":
        p=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
        if not p or p.approval_status!="APPROVED": raise HTTPException(403,"Doctor account is awaiting organizer approval.")
    if user.role=="hospital" and user.status!="active": raise HTTPException(403,"Hospital account is awaiting verification.")
    log_action(db,"LOGIN",user_id=user.id,ip_address=request.client.host if request.client else None)
    safe_event("login_success",user_id=user.id,role=user.role)
    return {"access_token":create_access_token(user),"token_type":"bearer","role":user.role,"user_id":user.id}

@router.post("/logout")
def logout(token:str=Depends(__import__("app.security",fromlist=["oauth2_scheme"]).oauth2_scheme),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    try: payload=__import__("jwt").decode(token,settings.JWT_SECRET,algorithms=[settings.JWT_ALGO]); exp=datetime.fromtimestamp(payload["exp"],tz=timezone.utc)
    except Exception: exp=datetime.now(timezone.utc)+timedelta(minutes=1)
    if not db.query(RevokedToken).filter(RevokedToken.token_jti==token_fingerprint(token)).first(): db.add(RevokedToken(token_jti=token_fingerprint(token),expires_at=exp)); db.commit()
    log_action(db,"LOGOUT",user_id=user.id); return {"message":"Logged out successfully."}

@router.post("/forgot-password",dependencies=[Depends(rate_limit("password_reset",settings.OTP_RATE_LIMIT,settings.RATE_LIMIT_WINDOW_MINUTES))])
def forgot_password(body:ForgotPasswordIn,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==body.email).first()
    if user:
        code=_issue_otp(db,body.email,"password_reset")
        try: send_email(body.email,"Q-Transplant — password reset OTP",f"Your one-time code is {code}. It expires in {settings.OTP_EXPIRY_MINUTES} minutes. If you did not request this, ignore this email.")
        except RuntimeError: pass
    return {"message":"If that email is registered, an OTP has been sent."}

@router.post("/reset-password",dependencies=[Depends(rate_limit("password_reset_verify",settings.OTP_RATE_LIMIT,settings.RATE_LIMIT_WINDOW_MINUTES))])
def reset_password(body:ResetPasswordIn,db:Session=Depends(get_db)):
    row=db.query(OTP).filter(OTP.email==body.email,OTP.used==False,OTP.purpose=="password_reset").order_by(OTP.created_at.desc()).first(); user=db.query(User).filter(User.email==body.email).first()
    if not row or not user or _is_expired(row.expires_at) or not verify_password(body.otp,row.code_hash): raise HTTPException(400,"Invalid or expired OTP.")
    user.hashed_password=hash_password(body.new_password); row.used=True
    db.query(OTP).filter(OTP.email==body.email,OTP.purpose=="password_reset",OTP.used==False).update({OTP.used:True},synchronize_session=False)
    db.commit(); log_action(db,"PASSWORD_RESET",user_id=user.id); return {"message":"Password updated successfully."}

@router.get("/me")
def me(user:User=Depends(get_current_user)): return {"id":user.id,"email":user.email,"role":user.role,"status":user.status,"email_verified":user.email_verified}
