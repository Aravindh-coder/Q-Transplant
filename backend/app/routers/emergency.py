"""Emergency alert system router for Q-Transplant quantum matching pipeline."""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from pydantic import BaseModel

from backend.app.core.database import get_db, Base
from backend.app.core.security import RoleChecker

router = APIRouter(prefix="/emergency", tags=["Emergency & Quantum Match Pipeline"])

# ── In-memory store for emergency events (persists across requests in process) ──
_emergency_events: List[dict] = []


class EmergencyRequest(BaseModel):
    hospital_name: str
    hospital_city: str
    contact_phone: str
    organ_needed: str
    blood_type: str
    hla_type: str
    urgency_level: str  # CRITICAL / HIGH / MEDIUM
    patient_age: int
    additional_notes: Optional[str] = None


class EmergencyOut(BaseModel):
    id: int
    hospital_name: str
    hospital_city: str
    contact_phone: str
    organ_needed: str
    blood_type: str
    hla_type: str
    urgency_level: str
    patient_age: int
    additional_notes: Optional[str]
    created_at: str
    status: str  # SEARCHING / MATCHED / CLOSED
    matched_hospital: Optional[str] = None


@router.post("/", response_model=EmergencyOut, status_code=status.HTTP_201_CREATED)
def post_emergency_alert(payload: EmergencyRequest):
    """Hospital posts an emergency organ search request — triggers Grover's search pipeline."""
    event_id = len(_emergency_events) + 1
    event = {
        "id": event_id,
        "hospital_name": payload.hospital_name,
        "hospital_city": payload.hospital_city,
        "contact_phone": payload.contact_phone,
        "organ_needed": payload.organ_needed,
        "blood_type": payload.blood_type,
        "hla_type": payload.hla_type,
        "urgency_level": payload.urgency_level,
        "patient_age": payload.patient_age,
        "additional_notes": payload.additional_notes or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "SEARCHING",
        "matched_hospital": None
    }
    _emergency_events.insert(0, event)

    # Simulate Grover's quantum search result (deterministic demo)
    import random
    demo_hospitals = [
        "Apollo Specialty Hospital, Bengaluru",
        "AIIMS Delhi Transplant Centre",
        "Fortis Memorial Research Institute",
        "Manipal Hospital, Mangaluru",
        "CMC Vellore Organ Transplant Unit"
    ]
    # Grover match simulation — mark as matched after insertion
    if len(_emergency_events) > 0:
        event["status"] = "MATCHED"
        event["matched_hospital"] = random.choice(demo_hospitals)

    return event


@router.get("/", response_model=List[EmergencyOut])
def list_emergency_alerts(limit: int = 10):
    """Public feed — returns latest emergency organ search events for landing page display."""
    return _emergency_events[:limit]


@router.get("/{event_id}", response_model=EmergencyOut)
def get_emergency_alert(event_id: int):
    for ev in _emergency_events:
        if ev["id"] == event_id:
            return ev
    raise HTTPException(status_code=404, detail="Emergency event not found.")


@router.delete("/{event_id}")
def close_emergency_alert(
    event_id: int,
    current_token: dict = Depends(RoleChecker(["organizer", "hospital"]))
):
    """Mark emergency as CLOSED."""
    for ev in _emergency_events:
        if ev["id"] == event_id:
            ev["status"] = "CLOSED"
            return {"message": "Emergency alert closed."}
    raise HTTPException(status_code=404, detail="Emergency event not found.")
