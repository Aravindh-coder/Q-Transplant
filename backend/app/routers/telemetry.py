from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.repositories.telemetry_repo import TelemetryRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.services.telemetry_service import TelemetryService
from backend.app.services.ai_risk_service import AIRiskService
from backend.app.schemas.domain import TelemetryPush, TelemetryOut

router = APIRouter(prefix="/telemetry", tags=["ESP32 Cold-Box Telemetry & GPS Tracking"])


@router.post("/push", response_model=TelemetryOut, status_code=status.HTTP_201_CREATED)
def push_sensor_telemetry(payload: TelemetryPush, db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    audit = AuditRepository(db)

    is_alarm, alarm_msg = TelemetryService.evaluate_cold_box(
        temp_celsius=payload.temp_celsius,
        battery_level=payload.battery_level
    )

    reading = repo.add_telemetry_reading(
        cold_box_id=payload.cold_box_id,
        lat=payload.lat,
        lng=payload.lng,
        temp_celsius=payload.temp_celsius,
        humidity_percent=payload.humidity_percent,
        battery_level=payload.battery_level,
        transport_id=payload.transport_id
    )

    if is_alarm:
        audit.log_action(
            user_id=None,
            action="TELEMETRY_ALARM",
            resource="ColdBox",
            details=f"Box {payload.cold_box_id}: {alarm_msg}"
        )

    return reading


@router.post("/emergency-trigger")
def trigger_cold_box_sos(cold_box_id: str = Form(...), reason: str = Form(...), db: Session = Depends(get_db)):
    """Called when emergency SOS button is pressed on ESP32 cold box hardware."""
    audit = AuditRepository(db)
    audit.log_action(
        user_id=None,
        action="HARDWARE_SOS_TRIGGER",
        resource="ESP32ColdBox",
        details=f"EMERGENCY BUTTON PRESSED on box {cold_box_id}: {reason}"
    )
    return {"status": "EMERGENCY_DISPATCHED", "cold_box_id": cold_box_id, "message": "Emergency dispatch alerted"}


@router.post("/ai-query")
def ask_ai_assistant(query: str = Form(...)):
    """Conversational query endpoint for integrated AI Transplant Assistant."""
    answer = AIRiskService.answer_ai_query(query, {})
    return {"query": query, "response": answer}


@router.get("/{cold_box_id}/latest", response_model=TelemetryOut)
def get_latest_sensor_data(cold_box_id: str, db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    data = repo.get_latest_telemetry(cold_box_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"No telemetry found for cold box {cold_box_id}")
    return data


@router.get("/{cold_box_id}/history", response_model=List[TelemetryOut])
def get_sensor_history(cold_box_id: str, limit: int = 50, db: Session = Depends(get_db)):
    repo = TelemetryRepository(db)
    return repo.get_telemetry_history(cold_box_id, limit=limit)
