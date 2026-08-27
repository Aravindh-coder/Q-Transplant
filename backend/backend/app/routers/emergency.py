"""
Q-Transplant — Emergency Network (production version)
Persists EmergencyRequest rows and writes audit log entries, on top of the
same WebSocket broadcast contract as the earlier prototype
(backend_emergency_ws.py) so the ESP32 firmware and app.html don't need to
change their message format.
"""
import json
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import HospitalProfile, EmergencyRequest, Device
from app.services.audit import log_action

router = APIRouter(prefix="/api/v1/emergency", tags=["emergency"])

CONNECTIONS: List[WebSocket] = []
DEVICE_TOKEN_HASHES: Dict[str, str] = {}  # hospital_id -> hashed device token, loaded at startup


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hospital_state(db: Session) -> dict:
    hospitals = db.query(HospitalProfile).all()
    out = {}
    for h in hospitals:
        open_req = (
            db.query(EmergencyRequest)
            .filter(EmergencyRequest.hospital_id == h.id, EmergencyRequest.status.notin_(["RESOLVED", "CANCELLED"]))
            .order_by(EmergencyRequest.created_at.desc())
            .first()
        )
        out[h.id] = {
            "name": h.hospital_name,
            "status": "idle" if not open_req else ("donor_found" if open_req.responding_hospital_id else "emergency"),
            "requirement": open_req.requirement if open_req else "",
        }
    return out


async def broadcast(payload: dict):
    dead = []
    for ws in CONNECTIONS:
        try:
            await ws.send_text(json.dumps(payload, default=str))
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in CONNECTIONS:
            CONNECTIONS.remove(ws)


async def broadcast_state():
    db = SessionLocal()
    try:
        await broadcast({"type": "state", "hospitals": _hospital_state(db), "timestamp": now_iso()})
    finally:
        db.close()


@router.websocket("/ws")
async def emergency_ws(websocket: WebSocket, hospital_id: str = "", device_token: str = ""):
    """
    Browser clients connect without a device_token. ESP32 firmware connects
    with ?hospital_id=...&device_token=... — verified against a hash, never
    a plaintext comparison. Reject anything unrecognized before accepting.
    """
    from app.security import verify_password  # local import avoids a circular import at module load

    if device_token:
        expected_hash = DEVICE_TOKEN_HASHES.get(hospital_id)
        if not expected_hash or not verify_password(device_token, expected_hash):
            await websocket.close(code=4401)
            return

    await websocket.accept()
    CONNECTIONS.append(websocket)

    db = SessionLocal()
    try:
        await websocket.send_text(json.dumps({"type": "state", "hospitals": _hospital_state(db), "timestamp": now_iso()}))
    finally:
        db.close()

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            hid = msg.get("hospital_id")
            if not hid:
                continue

            db = SessionLocal()
            try:
                hospital = db.query(HospitalProfile).filter(HospitalProfile.id == hid).first()
                if not hospital:
                    continue

                if msg["type"] == "emergency":
                    req = EmergencyRequest(hospital_id=hid, requirement=msg.get("requirement", ""), status="NOTIFIED")
                    db.add(req)
                    db.commit()
                    log_action(db, "EMERGENCY_CREATED", target=hid, meta={"requirement": msg.get("requirement", "")})

                elif msg["type"] == "requirement_update":
                    open_req = (
                        db.query(EmergencyRequest)
                        .filter(EmergencyRequest.hospital_id == hid, EmergencyRequest.status.notin_(["RESOLVED", "CANCELLED"]))
                        .order_by(EmergencyRequest.created_at.desc()).first()
                    )
                    if open_req:
                        open_req.requirement = msg.get("requirement", "")
                        db.commit()

                elif msg["type"] == "donor_found":
                    target_id = msg.get("target_hospital_id")
                    open_req = (
                        db.query(EmergencyRequest)
                        .filter(EmergencyRequest.hospital_id == target_id, EmergencyRequest.status.notin_(["RESOLVED", "CANCELLED"]))
                        .order_by(EmergencyRequest.created_at.desc()).first()
                    )
                    if open_req:
                        open_req.responding_hospital_id = hid
                        open_req.status = "ACKNOWLEDGED"
                        db.commit()
                        log_action(db, "MATCH_GENERATED", target=target_id, meta={"responding_hospital": hid})

                elif msg["type"] == "acknowledge":
                    open_req = (
                        db.query(EmergencyRequest)
                        .filter(EmergencyRequest.hospital_id == hid, EmergencyRequest.status.notin_(["RESOLVED", "CANCELLED"]))
                        .order_by(EmergencyRequest.created_at.desc()).first()
                    )
                    if open_req:
                        open_req.status = "RESOLVED"
                        open_req.resolved_at = datetime.now(timezone.utc)
                        db.commit()
                        log_action(db, "EMERGENCY_ACKNOWLEDGED", target=hid)

                device = db.query(Device).filter(Device.hospital_id == hid).first()
                if device:
                    device.last_seen = datetime.now(timezone.utc)
                    device.connection_status = "online"
                    db.commit()
            finally:
                db.close()

            await broadcast_state()

    except WebSocketDisconnect:
        if websocket in CONNECTIONS:
            CONNECTIONS.remove(websocket)
