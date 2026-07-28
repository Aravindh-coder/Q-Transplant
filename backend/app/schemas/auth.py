from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = Field(..., description="Role: organizer, doctor, hospital, donor, patient")
    phone: Optional[str] = None
    
    # Specific fields based on role
    license_number: Optional[str] = None  # for hospital or doctor
    city: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None
    blood_type: Optional[str] = None
    hla_type: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    target_organ: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: str
    is_approved: bool


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
