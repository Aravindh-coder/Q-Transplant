import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
import enum
from backend.app.core.database import Base


class UserRole(str, enum.Enum):
    ORGANIZER = "organizer"
    DOCTOR = "doctor"
    HOSPITAL = "hospital"
    DONOR = "donor"
    PATIENT = "patient"


class OrganStatus(str, enum.Enum):
    AVAILABLE = "available"
    MATCHED = "matched"
    IN_TRANSIT = "in_transit"
    TRANSPLANTED = "transplanted"
    EXPIRED = "expired"


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.PATIENT.value, nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    hospital = relationship("Hospital", back_populates="user", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    donor = relationship("Donor", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    reset_tokens = relationship("PasswordReset", back_populates="user")


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    license_number = Column(String(100), unique=True, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False, default=12.9716)
    lng = Column(Float, nullable=False, default=77.5946)
    contact_phone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="hospital")
    doctors = relationship("Doctor", back_populates="hospital")
    ambulances = relationship("Ambulance", back_populates="hospital")
    icu_occupancy = relationship("ICUOccupancy", back_populates="hospital", uselist=False)
    blood_inventory = relationship("BloodInventory", back_populates="hospital")
    operation_theatres = relationship("OperationTheatre", back_populates="hospital")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    medical_license = Column(String(100), unique=True, nullable=False)
    specialization = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    certificate_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="doctor")
    hospital = relationship("Hospital", back_populates="doctors")
    patients = relationship("Patient", back_populates="doctor")
    donors = relationship("Donor", back_populates="doctor")


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    blood_type = Column(String(10), nullable=False)
    hla_type = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    medical_history = Column(Text, nullable=True)
    status = Column(String(50), default="registered")
    qr_code_token = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="donor")
    doctor = relationship("Doctor", back_populates="donors")
    organs = relationship("Organ", back_populates="donor")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    blood_type = Column(String(10), nullable=False)
    hla_type = Column(String(100), nullable=False)
    target_organ = Column(String(50), nullable=False)
    urgency_score = Column(Integer, default=5, nullable=False)
    status = Column(String(50), default="waiting_list")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="patient")
    doctor = relationship("Doctor", back_populates="patients")
    matches = relationship("Match", back_populates="patient")


class Organ(Base):
    __tablename__ = "organs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    donor_id = Column(Integer, ForeignKey("donors.id"), nullable=False)
    organ_type = Column(String(50), nullable=False)
    blood_type = Column(String(10), nullable=False)
    hla_type = Column(String(100), nullable=False)
    max_ischemia_hours = Column(Float, default=6.0)
    cold_box_id = Column(String(100), nullable=False, default="BOX-ESP32-001")
    status = Column(String(50), default=OrganStatus.AVAILABLE.value)
    harvested_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    donor = relationship("Donor", back_populates="organs")
    matches = relationship("Match", back_populates="organ")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    organ_id = Column(Integer, ForeignKey("organs.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    distance_km = Column(Float, default=15.0)
    status = Column(String(50), default=MatchStatus.PENDING.value)
    match_rationale = Column(Text, nullable=True)
    matched_at = Column(DateTime, default=datetime.datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)

    organ = relationship("Organ", back_populates="matches")
    patient = relationship("Patient", back_populates="matches")
    transports = relationship("Transport", back_populates="match")


class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    vehicle_number = Column(String(50), unique=True, nullable=False)
    driver_name = Column(String(100), nullable=False)
    driver_phone = Column(String(50), nullable=False)
    current_lat = Column(Float, default=12.9716)
    current_lng = Column(Float, default=77.5946)
    is_available = Column(Boolean, default=True)

    hospital = relationship("Hospital", back_populates="ambulances")
    transports = relationship("Transport", back_populates="ambulance")


class Transport(Base):
    __tablename__ = "transports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    ambulance_id = Column(Integer, ForeignKey("ambulances.id"), nullable=False)
    origin_address = Column(String(255), nullable=False)
    destination_address = Column(String(255), nullable=False)
    status = Column(String(50), default="dispatched")
    eta_minutes = Column(Integer, default=45)
    dispatched_at = Column(DateTime, default=datetime.datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

    match = relationship("Match", back_populates="transports")
    ambulance = relationship("Ambulance", back_populates="transports")
    gps_locations = relationship("GPSLocation", back_populates="transport")


class GPSLocation(Base):
    __tablename__ = "gps_locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transport_id = Column(Integer, ForeignKey("transports.id"), nullable=True)
    cold_box_id = Column(String(100), nullable=False, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    temp_celsius = Column(Float, nullable=False, default=4.0)
    humidity_percent = Column(Float, nullable=False, default=85.0)
    battery_level = Column(Float, nullable=False, default=98.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    transport = relationship("Transport", back_populates="gps_locations")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    refresh_token = Column(String(512), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_entity = Column(String(100), nullable=False)
    target_id = Column(Integer, nullable=False)
    requested_by = Column(String(255), nullable=False)
    approved_by = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reset_tokens")


class ICUOccupancy(Base):
    __tablename__ = "icu_occupancies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), unique=True, nullable=False)
    total_beds = Column(Integer, default=20, nullable=False)
    occupied_beds = Column(Integer, default=14, nullable=False)
    ventilators_available = Column(Integer, default=6, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    hospital = relationship("Hospital", back_populates="icu_occupancy")


class BloodInventory(Base):
    __tablename__ = "blood_inventories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    blood_type = Column(String(10), nullable=False)
    units_available = Column(Integer, default=10, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    hospital = relationship("Hospital", back_populates="blood_inventory")


class OperationTheatre(Base):
    __tablename__ = "operation_theatres"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(50), default="available")  # available, occupied, maintenance
    current_procedure = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    hospital = relationship("Hospital", back_populates="operation_theatres")
