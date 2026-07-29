"""Emergency alert system router for Q-Transplant quantum matching pipeline."""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.app.core.database import get_db, Base
from backend.app.core.security import RoleChecker

router = APIRouter(prefix="/emergency", tags=["Emergency & Quantum Match Pipeline"])

# ── Single current system state — updated by each ESP32 button press ──────────
# status values: IDLE | SEARCHING | DONOR_MATCHED | ACKNOWLEDGED
_current_state: dict = {
    "status": "IDLE",
    "hospital_name": None,
    "hospital_city": None,
    "contact_phone": None,
    "organ_needed": None,
    "blood_type": None,
    "hla_type": None,
    "urgency_level": None,
    "patient_age": None,
    "donor_hospital": None,
    "donor_organ": None,
    "donor_blood_type": None,
    "cold_box_id": None,
    "updated_at": None,
    "message": "System monitoring 15 hospitals. All clear.",
}

# ── History log (kept for organizer audit, not shown on landing page) ──────────
_emergency_events: List[dict] = []


class EmergencyRequest(BaseModel):
    hospital_name: str
    hospital_city: str
    contact_phone: str
    organ_needed: str
    blood_type: str
    hla_type: str
    urgency_level: str
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
    status: str
    matched_hospital: Optional[str] = None


# ── GET: Current live state (polled by landing page every 2.5s) ───────────────
@router.get("/current-state")
def get_current_state():
    """Returns the single current system state — reacts to ESP32 button presses."""
    return _current_state


# ── POST: Emergency SOS Button (ESP32 GPIO 13) ────────────────────────────────
@router.post("/dispatch", status_code=status.HTTP_201_CREATED)
def hardware_emergency_dispatch(payload: dict):
    """ESP32 GPIO 13 pressed — set system state to SEARCHING emergency."""
    now = datetime.now(timezone.utc).isoformat()

    _current_state.update({
        "status": "SEARCHING",
        "hospital_name": payload.get("hospital_name", "Apollo Specialty Hospital"),
        "hospital_city": payload.get("hospital_city", "Bengaluru"),
        "contact_phone": payload.get("contact_phone", "080-4444-1111"),
        "organ_needed": payload.get("organ_type", "Heart"),
        "blood_type": payload.get("blood_type", "O+"),
        "hla_type": payload.get("hla_type", "A2,B7,DR4"),
        "urgency_level": "CRITICAL",
        "patient_age": payload.get("patient_age", 45),
        "cold_box_id": payload.get("cold_box_id", "BOX-ESP32-001"),
        "donor_hospital": None,
        "donor_organ": None,
        "donor_blood_type": None,
        "updated_at": now,
        "message": "🚨 EMERGENCY ACTIVE — Grover's Quantum Search running across 15 hospital nodes...",
    })

    # Save to history log
    _emergency_events.insert(0, {**_current_state, "id": len(_emergency_events) + 1, "created_at": now})

    return {"status": "EMERGENCY_DISPATCHED", "state": _current_state}


# ── POST: Manual Emergency Form (landing page button) ─────────────────────────
@router.post("/", response_model=EmergencyOut, status_code=status.HTTP_201_CREATED)
def post_emergency_alert(payload: EmergencyRequest):
    """Manual emergency submission from landing page form."""
    now = datetime.now(timezone.utc).isoformat()

    _current_state.update({
        "status": "SEARCHING",
        "hospital_name": payload.hospital_name,
        "hospital_city": payload.hospital_city,
        "contact_phone": payload.contact_phone,
        "organ_needed": payload.organ_needed,
        "blood_type": payload.blood_type,
        "hla_type": payload.hla_type,
        "urgency_level": payload.urgency_level,
        "patient_age": payload.patient_age,
        "donor_hospital": None,
        "donor_organ": None,
        "donor_blood_type": None,
        "cold_box_id": "WEB-FORM",
        "updated_at": now,
        "message": "🚨 EMERGENCY ACTIVE — Grover's Quantum Search running...",
    })

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
        "created_at": now,
        "status": "SEARCHING",
        "matched_hospital": None,
    }
    _emergency_events.insert(0, event)
    return event


# ── POST: Donor Available Button (ESP32 GPIO 12) ──────────────────────────────
@router.post("/donor-available")
def register_donor_available(payload: dict):
    """ESP32 GPIO 12 pressed — another hospital has a donor organ ready."""
    donor_hospital = payload.get("hospital_name", "Fortis Healthcare, Bengaluru")
    organ_type = payload.get("organ_type", "Heart")
    blood_type = payload.get("blood_type", "O+")
    now = datetime.now(timezone.utc).isoformat()

    _current_state.update({
        "status": "DONOR_MATCHED",
        "donor_hospital": donor_hospital,
        "donor_organ": organ_type,
        "donor_blood_type": blood_type,
        "updated_at": now,
        "message": f"💚 DONOR MATCH FOUND — {donor_hospital} has {organ_type} ({blood_type}) available. Transport team dispatched!",
    })

    return {
        "status": "DONOR_MATCHED",
        "donor_hospital": donor_hospital,
        "organ_type": organ_type,
        "blood_type": blood_type,
        "state": _current_state,
        "message": f"Donor availability from {donor_hospital} broadcasted to all hospital nodes!",
    }


# ── POST: Acknowledge Button (ESP32 GPIO 14) ──────────────────────────────────
@router.post("/acknowledge")
def acknowledge_emergency(payload: Optional[dict] = None):
    """ESP32 GPIO 14 pressed — hospital crew acknowledges, emergency stops."""
    now = datetime.now(timezone.utc).isoformat()

    _current_state.update({
        "status": "ACKNOWLEDGED",
        "updated_at": now,
        "message": "✔ ACKNOWLEDGED — Emergency siren stopped. Hospital crew confirmed. System returning to normal.",
    })

    return {
        "status": "ACKNOWLEDGED",
        "emergency_stopped": True,
        "state": _current_state,
        "message": "Emergency acknowledged and stopped!",
    }


# ── POST: Reset to IDLE ───────────────────────────────────────────────────────
@router.post("/reset")
def reset_system():
    """Reset system state to IDLE (all clear)."""
    _current_state.update({
        "status": "IDLE",
        "hospital_name": None,
        "hospital_city": None,
        "contact_phone": None,
        "organ_needed": None,
        "blood_type": None,
        "hla_type": None,
        "urgency_level": None,
        "patient_age": None,
        "donor_hospital": None,
        "donor_organ": None,
        "donor_blood_type": None,
        "cold_box_id": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "message": "System monitoring 15 hospitals. All clear.",
    })
    return {"status": "IDLE", "message": "System reset to idle."}


# ── GET: History log (for organizer dashboard) ────────────────────────────────
@router.get("/", response_model=List[EmergencyOut])
def list_emergency_alerts(limit: int = 10):
    """Audit history of past emergency events."""
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
    """Mark emergency as CLOSED in history."""
    for ev in _emergency_events:
        if ev["id"] == event_id:
            ev["status"] = "CLOSED"
            return {"message": "Emergency alert closed."}
    raise HTTPException(status_code=404, detail="Emergency event not found.")
