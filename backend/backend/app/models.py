"""
Q-Transplant — Database Models
All primary keys are UUID strings. Foreign keys reference users.id wherever a
row belongs to a specific account, so role-based access can always be checked
against the same identity table.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, DateTime, Boolean, Float, Integer, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


def uid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------- identity ----------------
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # donor | doctor | hospital | organizer
    full_name = Column(String, nullable=True)
    status = Column(String, default="active")  # active | pending | suspended
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)


class OTP(Base):
    __tablename__ = "otps"
    id = Column(String, primary_key=True, default=uid)
    email = Column(String, index=True, nullable=False)
    code_hash = Column(String, nullable=False)
    purpose = Column(String, default="password_reset")  # password_reset | email_verify
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)


# ---------------- role profiles ----------------
class DonorProfile(Base):
    __tablename__ = "donor_profiles"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    date_of_birth = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    blood_group = Column(String, nullable=False)  # O+, A+, B+, AB+, O-, A-, B-, AB-
    organs_available = Column(JSON, default=list)  # ["kidney","liver_partial",...]
    hla_a = Column(String, nullable=True)
    hla_b = Column(String, nullable=True)
    hla_c = Column(String, nullable=True)
    hla_dr = Column(String, nullable=True)
    hla_dq = Column(String, nullable=True)
    availability_status = Column(String, default="active")  # active | inactive
    hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=True)
    verification_status = Column(String, default="pending")  # pending | verified
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    license_number = Column(String, nullable=False)
    specialty = Column(String, nullable=True)
    photo_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    certificate_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=True)
    approval_status = Column(String, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime, default=now)


class HospitalProfile(Base):
    __tablename__ = "hospital_profiles"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    hospital_name = Column(String, nullable=False)
    hospital_code = Column(String, unique=True, nullable=False)  # e.g. HOSP-CHN-001
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    license_document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    verification_status = Column(String, default="pending")  # pending | verified
    created_at = Column(DateTime, default=now)


# ---------------- clinical ----------------
class Patient(Base):
    __tablename__ = "patients"
    id = Column(String, primary_key=True, default=uid)
    hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("doctor_profiles.id"), nullable=False)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    blood_group = Column(String, nullable=False)
    required_organ = Column(String, nullable=False)
    hla_a = Column(String, nullable=True)
    hla_b = Column(String, nullable=True)
    hla_c = Column(String, nullable=True)
    hla_dr = Column(String, nullable=True)
    hla_dq = Column(String, nullable=True)
    urgency = Column(String, default="MEDIUM")  # LOW|MEDIUM|HIGH|CRITICAL|EMERGENCY
    waiting_since = Column(DateTime, default=now)
    waitlist_status = Column(String, default="waiting")  # waiting|matched|transplanted|removed
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


class TransplantCase(Base):
    __tablename__ = "transplant_cases"
    id = Column(String, primary_key=True, default=uid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=False)
    donor_id = Column(String, ForeignKey("donor_profiles.id"), nullable=True)
    stage = Column(String, default="CREATED")
    # CREATED -> MEDICAL_REVIEW -> MATCH_SEARCH -> CANDIDATE_FOUND -> DOCTOR_REVIEW
    # -> HOSPITAL_COORDINATION -> APPROVED_FOR_PROCEDURE -> PROCEDURE_SCHEDULED -> COMPLETED
    # alt: CANCELLED | ON_HOLD | REJECTED
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)


class MatchRequest(Base):
    __tablename__ = "match_requests"
    id = Column(String, primary_key=True, default=uid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    requested_by = Column(String, ForeignKey("users.id"), nullable=False)
    organ = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending|completed|failed
    created_at = Column(DateTime, default=now)


class MatchResult(Base):
    __tablename__ = "match_results"
    id = Column(String, primary_key=True, default=uid)
    match_request_id = Column(String, ForeignKey("match_requests.id"), nullable=False)
    donor_id = Column(String, ForeignKey("donor_profiles.id"), nullable=False)
    blood_compatible = Column(Boolean, nullable=False)
    hla_score = Column(Float, nullable=False)
    organ_compatible = Column(Boolean, nullable=False)
    urgency_at_match = Column(String, nullable=False)
    overall_score = Column(Float, nullable=False)
    explanation = Column(JSON, default=dict)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=now)


# ---------------- emergency / devices ----------------
class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"
    id = Column(String, primary_key=True, default=uid)
    hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=False)
    raised_by = Column(String, ForeignKey("users.id"), nullable=True)
    requirement = Column(String, nullable=True)
    status = Column(String, default="CREATED")
    # CREATED -> NOTIFIED -> ACKNOWLEDGED -> PROCESSING -> RESOLVED | CANCELLED
    responding_hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=True)
    created_at = Column(DateTime, default=now)
    resolved_at = Column(DateTime, nullable=True)


class Device(Base):
    __tablename__ = "devices"
    id = Column(String, primary_key=True, default=uid)
    hospital_id = Column(String, ForeignKey("hospital_profiles.id"), nullable=False)
    device_token_hash = Column(String, nullable=False)
    firmware_version = Column(String, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    connection_status = Column(String, default="offline")  # online|offline
    created_at = Column(DateTime, default=now)


# ---------------- documents / notifications / audit ----------------
class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=uid)
    owner_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    kind = Column(String, nullable=False)  # license|certificate|medical_report|id_proof|hla_typing
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)  # never a public URL
    verification_status = Column(String, default="pending")  # pending|verified|rejected
    uploaded_at = Column(DateTime, default=now)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True, default=uid)
    recipient_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # EMAIL|IN_APP|REAL_TIME|ESP32
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String, default="normal")  # low|normal|high|critical
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=now)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # LOGIN, DOCTOR_APPROVED, MATCH_GENERATED, ...
    target = Column(String, nullable=True)
    meta = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)
