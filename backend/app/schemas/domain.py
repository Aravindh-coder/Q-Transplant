from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    is_approved: bool
    created_at: datetime


class ApprovalAction(BaseModel):
    user_id: int
    approve: bool
    reason: Optional[str] = ""


class HospitalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    license_number: str
    city: str
    state: str
    address: str
    lat: float
    lng: float
    contact_phone: str


class DoctorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medical_license: str
    specialization: str
    department: str
    phone: str


class DonorCreate(BaseModel):
    blood_type: str
    hla_type: str
    age: int
    gender: str
    medical_history: Optional[str] = None


class DonorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    blood_type: str
    hla_type: str
    age: int
    gender: str
    medical_history: Optional[str]
    status: str
    created_at: datetime


class PatientCreate(BaseModel):
    blood_type: str
    hla_type: str
    target_organ: str
    urgency_score: int = 5


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    blood_type: str
    hla_type: str
    target_organ: str
    urgency_score: int
    status: str
    created_at: datetime


class OrganCreate(BaseModel):
    donor_id: int
    organ_type: str
    blood_type: str
    hla_type: str
    max_ischemia_hours: float = 6.0
    cold_box_id: str = "BOX-ESP32-001"


class OrganOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    donor_id: int
    organ_type: str
    blood_type: str
    hla_type: str
    max_ischemia_hours: float
    cold_box_id: str
    status: str
    harvested_at: datetime


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organ_id: int
    patient_id: int
    compatibility_score: float
    distance_km: float
    status: str
    matched_at: datetime
    organ: Optional[OrganOut] = None
    patient: Optional[PatientOut] = None


class TelemetryPush(BaseModel):
    cold_box_id: str
    lat: float
    lng: float
    temp_celsius: float
    humidity_percent: float
    battery_level: float
    transport_id: Optional[int] = None


class TelemetryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cold_box_id: str
    lat: float
    lng: float
    temp_celsius: float
    humidity_percent: float
    battery_level: float
    timestamp: datetime


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    action: str
    resource: str
    details: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime
