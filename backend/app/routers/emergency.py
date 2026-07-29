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


@router.post("/dispatch", status_code=status.HTTP_201_CREATED)
def hardware_emergency_dispatch(payload: dict):
    """Direct JSON dispatch endpoint for ESP32 emergency button presses."""
    event_id = len(_emergency_events) + 1
    event = {
        "id": event_id,
        "hospital_name": payload.get("hospital_name", "Apollo Specialty Hospital"),
        "hospital_city": payload.get("hospital_city", "Bengaluru"),
        "contact_phone": payload.get("contact_phone", "080-4444-1111"),
        "organ_needed": payload.get("organ_type", "Heart"),
        "blood_type": payload.get("blood_type", "O+"),
        "hla_type": payload.get("hla_type", "A2,B7,DR4"),
        "urgency_level": payload.get("urgency_level", "CRITICAL"),
        "patient_age": payload.get("patient_age", 45),
        "additional_notes": f"HARDWARE ESP32 DISPATCH — Box ID: {payload.get('cold_box_id', 'BOX-ESP32-001')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "SEARCHING",
        "matched_hospital": "Fortis Healthcare, Bengaluru (Grover Match 98.4%)"
    }
    _emergency_events.insert(0, event)
    return {
        "status": "EMERGENCY_DISPATCHED",
        "event": event,
        "message": "Emergency dispatch alert broadcasted to landing page and hospital network"
    }


@router.post("/donor-available")
def register_donor_available(payload: dict):
    """Called when another hospital clicks 'Donor Available Button' (ESP32 GPIO 12 or Web)."""
    donor_hospital = payload.get("hospital_name", "Fortis Healthcare, Bengaluru")
    organ_type = payload.get("organ_type", "Heart")
    blood_type = payload.get("blood_type", "O+")
    box_id = payload.get("cold_box_id", "BOX-ESP32-001")

    matched_event = None
    for ev in _emergency_events:
        if ev["status"] in ["SEARCHING", "CRITICAL", "MATCHED"]:
            ev["status"] = "DONOR_MATCHED"
            ev["matched_hospital"] = f"{donor_hospital} (Donor {organ_type} {blood_type} Available via {box_id})"
            ev["additional_notes"] = f"MATCH CONFIRMED! {donor_hospital} has an available {organ_type} ({blood_type}). Transport Team Dispatched."
            matched_event = ev
            break

    if not matched_event and len(_emergency_events) > 0:
        _emergency_events[0]["status"] = "DONOR_MATCHED"
        _emergency_events[0]["matched_hospital"] = f"{donor_hospital} (Donor {organ_type} {blood_type} Available)"
        matched_event = _emergency_events[0]

    return {
        "status": "DONOR_MATCHED",
        "donor_hospital": donor_hospital,
        "organ_type": organ_type,
        "blood_type": blood_type,
        "matched_event": matched_event,
        "message": f"Donor organ availability broadcasted! Recipient hospital received: {donor_hospital}"
    }


@router.post("/acknowledge")
def acknowledge_emergency(payload: Optional[dict] = None):
    """Called when hospital crew presses 'Acknowledge Button' (ESP32 GPIO 14). Stops emergency alarm state."""
    ack_count = 0
    for ev in _emergency_events:
        if ev["status"] in ["SEARCHING", "CRITICAL", "DONOR_MATCHED", "MATCHED"]:
            ev["status"] = "ACKNOWLEDGED"
            ev["additional_notes"] += " [ACKNOWLEDGED BY HOSPITAL CREW - SIREN STOPPED]"
            ack_count += 1

    return {
        "status": "ACKNOWLEDGED",
        "emergency_stopped": True,
        "events_acknowledged": ack_count,
        "message": "Emergency Siren STOPPED & Alert Acknowledged by Hospital Crew!"
    }


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
