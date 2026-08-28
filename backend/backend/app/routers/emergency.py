"""Q-Transplant emergency coordination and authenticated ESP32 real-time state."""
import json
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models import User, HospitalProfile, EmergencyRequest, Device, DoctorProfile
from app.security import require_role, verify_password
from app.services.audit import log_action
from app.services.notifications import notify_role, notify_organizer

router = APIRouter(prefix="/api/v1/emergency", tags=["emergency"])
CONNECTIONS: List[WebSocket] = []
TERMINAL = {"RESOLVED", "CANCELLED"}


def now_utc(): return datetime.now(timezone.utc)
def now_iso(): return now_utc().isoformat()


def _hospital_state(db):
    out = {}
    for h in db.query(HospitalProfile).all():
        req = (db.query(EmergencyRequest)
               .filter(EmergencyRequest.hospital_id == h.id,
                       EmergencyRequest.status.notin_(list(TERMINAL)))
               .order_by(EmergencyRequest.created_at.desc()).first())
        out[h.id] = {
            "name": h.hospital_name,
            "status": "idle" if not req else ("donor_found" if req.responding_hospital_id else "emergency"),
            "requirement": req.requirement if req else "",
            "emergency_status": req.status if req else None,
        }
    return out


async def broadcast(payload):
    dead = []
    for ws in list(CONNECTIONS):
        try: await ws.send_text(json.dumps(payload, default=str))
        except Exception: dead.append(ws)
    for ws in dead:
        if ws in CONNECTIONS: CONNECTIONS.remove(ws)


async def broadcast_state():
    db = SessionLocal()
    try: await broadcast({"type": "state", "hospitals": _hospital_state(db), "timestamp": now_iso()})
    finally: db.close()


class EmergencyIn(BaseModel):
    requirement: str = Field(min_length=1, max_length=2000)


@router.post("/create")
async def create_emergency(body: EmergencyIn, user: User = Depends(require_role("doctor", "hospital")), db: Session = Depends(get_db)):
    hospital_id = None
    if user.role == "hospital":
        h = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        hospital_id = h.id if h else None
    else:
        d = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
        hospital_id = d.hospital_id if d else None
    if not hospital_id: raise HTTPException(400, "Your account is not linked to a hospital.")
    req = EmergencyRequest(hospital_id=hospital_id, raised_by=user.id, requirement=body.requirement, status="NOTIFIED")
    db.add(req); db.flush()
    notify_role(db, "hospital", "Emergency request", "A transplant emergency requires attention: " + body.requirement, "urgent", True)
    notify_role(db, "doctor", "Emergency request", "A transplant emergency requires attention: " + body.requirement, "urgent", True)
    log_action(db, "EMERGENCY_CREATED", user_id=user.id, target=req.id, meta={"requirement": body.requirement})
    db.commit()
    notify_organizer("Q-Transplant — emergency request", f"Emergency raised by {user.full_name}: {body.requirement}")
    await broadcast_state()
    return {"id": req.id, "status": req.status, "hospital_id": hospital_id}


@router.get("")
def list_emergencies(user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    q = db.query(EmergencyRequest).order_by(EmergencyRequest.created_at.desc())
    if user.role == "hospital":
        h = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        if h: q = q.filter(EmergencyRequest.hospital_id == h.id)
    return [{"id": x.id, "hospital_id": x.hospital_id, "requirement": x.requirement,
             "status": x.status, "created_at": x.created_at, "resolved_at": x.resolved_at}
            for x in q.limit(100).all()]


@router.websocket("/ws")
async def emergency_ws(websocket: WebSocket, hospital_id: str = "", device_token: str = ""):
    """Authenticated ESP32 channel using persisted Device token hashes."""
    if not hospital_id or not device_token:
        await websocket.close(code=4401); return

    db = SessionLocal(); device = None
    try:
        for candidate in db.query(Device).filter(Device.hospital_id == hospital_id).all():
            try:
                if verify_password(device_token, candidate.device_token_hash):
                    device = candidate; break
            except Exception:
                continue
        if device is None:
            await websocket.close(code=4401); return
        device.last_seen = now_utc(); device.connection_status = "online"; db.commit()
    finally:
        db.close()

    await websocket.accept(); CONNECTIONS.append(websocket)
    db = SessionLocal()
    try: await websocket.send_text(json.dumps({"type": "state", "hospitals": _hospital_state(db), "timestamp": now_iso()}))
    finally: db.close()

    try:
        while True:
            msg = json.loads(await websocket.receive_text())
            hid = msg.get("hospital_id")
            if hid != hospital_id:
                await websocket.send_text(json.dumps({"type": "error", "code": "DEVICE_HOSPITAL_MISMATCH"})); continue
            db = SessionLocal()
            try:
                device_db = db.query(Device).filter(Device.id == device.id, Device.hospital_id == hospital_id).first()
                if not device_db:
                    await websocket.close(code=4403); return
                device_db.last_seen = now_utc(); device_db.connection_status = "online"
                kind = msg.get("type")

                if kind == "heartbeat":
                    device_db.firmware_version = msg.get("firmware_version") or device_db.firmware_version
                    db.commit()
                elif kind == "emergency":
                    requirement = str(msg.get("requirement", "")).strip()[:2000] or "Emergency assistance required"
                    req = EmergencyRequest(hospital_id=hid, requirement=requirement, status="NOTIFIED")
                    db.add(req); db.flush()
                    notify_role(db, "hospital", "Emergency request", "Emergency requirement: " + requirement, "urgent", True)
                    notify_role(db, "doctor", "Emergency request", "Emergency requirement: " + requirement, "urgent", True)
                    log_action(db, "EMERGENCY_CREATED", target=req.id, meta={"source": "esp32", "device_id": device.id})
                    db.commit(); notify_organizer("Q-Transplant — emergency request", "Hospital emergency: " + requirement)
                elif kind == "requirement_update":
                    req = (db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id == hid,
                            EmergencyRequest.status.notin_(list(TERMINAL))).order_by(EmergencyRequest.created_at.desc()).first())
                    if req: req.requirement = str(msg.get("requirement", "")).strip()[:2000]; db.commit()
                elif kind == "donor_found":
                    target = msg.get("target_hospital_id")
                    req = (db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id == target,
                            EmergencyRequest.status.notin_(list(TERMINAL))).order_by(EmergencyRequest.created_at.desc()).first()) if target else None
                    if req:
                        req.responding_hospital_id = hid; req.status = "ACKNOWLEDGED"
                        log_action(db, "EMERGENCY_ACKNOWLEDGED", target=req.id, meta={"responding_hospital": hid, "source": "esp32"})
                        db.commit(); notify_organizer("Q-Transplant — emergency response", "A hospital has responded to an emergency request.")
                elif kind == "acknowledge":
                    req = (db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id == hid,
                            EmergencyRequest.status.notin_(list(TERMINAL))).order_by(EmergencyRequest.created_at.desc()).first())
                    if req and req.status in {"CREATED", "NOTIFIED"}:
                        req.status = "ACKNOWLEDGED"
                        log_action(db, "EMERGENCY_ACKNOWLEDGED", target=req.id, meta={"device_id": device.id, "source": "esp32"}); db.commit()
                elif kind == "processing":
                    req = (db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id == hid,
                            EmergencyRequest.status.notin_(list(TERMINAL))).order_by(EmergencyRequest.created_at.desc()).first())
                    if req and req.status == "ACKNOWLEDGED": req.status = "PROCESSING"; db.commit()
                elif kind == "resolve":
                    req = (db.query(EmergencyRequest).filter(EmergencyRequest.hospital_id == hid,
                            EmergencyRequest.status == "PROCESSING").order_by(EmergencyRequest.created_at.desc()).first())
                    if req:
                        req.status = "RESOLVED"; req.resolved_at = now_utc()
                        log_action(db, "EMERGENCY_RESOLVED", target=req.id, meta={"device_id": device.id, "source": "esp32"}); db.commit()
            finally: db.close()
            await broadcast_state()
    except WebSocketDisconnect:
        if websocket in CONNECTIONS: CONNECTIONS.remove(websocket)
        db = SessionLocal()
        try:
            d = db.query(Device).filter(Device.id == device.id).first()
            if d: d.connection_status = "offline"; d.last_seen = now_utc(); db.commit()
        finally: db.close()
