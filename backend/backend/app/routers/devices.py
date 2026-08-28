import secrets
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Device, HospitalProfile
from app.security import require_role, hash_password, verify_password
from app.services.audit import log_action
from app.utils import to_dict_list

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

def authenticate_device(device_id: str, token: str, db: Session):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device or not token or not verify_password(token, device.device_token_hash):
        raise HTTPException(401, "Invalid device credentials")
    return device

@router.post("/provision")
def provision_device(hospital_id: str, firmware_version: str = "1.0.0", user: User = Depends(require_role("organizer", "hospital")), db: Session = Depends(get_db)):
    hospital = db.query(HospitalProfile).filter(HospitalProfile.id == hospital_id).first()
    if not hospital: raise HTTPException(404, "Hospital not found.")
    raw_token = secrets.token_urlsafe(24)
    device = Device(hospital_id=hospital_id, device_token_hash=hash_password(raw_token), firmware_version=firmware_version, connection_status="offline")
    db.add(device); db.commit(); db.refresh(device)
    log_action(db, "DEVICE_PROVISIONED", user_id=user.id, target=hospital_id)
    return {"device_id": device.id, "device_token": raw_token, "warning": "Token shown once. Store it securely in the ESP32 firmware."}

@router.post("/{device_id}/heartbeat")
def heartbeat(device_id: str, x_device_token: str = Header(None), db: Session = Depends(get_db)):
    device = authenticate_device(device_id, x_device_token, db)
    from datetime import datetime, timezone
    device.last_seen = datetime.now(timezone.utc); device.connection_status = "online"
    db.commit()
    return {"device_id": device.id, "connection_status": "online", "last_seen": device.last_seen}

@router.get("")
def list_devices(user: User = Depends(require_role("organizer", "hospital")), db: Session = Depends(get_db)):
    q = db.query(Device)
    if user.role == "hospital":
        hospital = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
        if not hospital: return []
        q = q.filter(Device.hospital_id == hospital.id)
    return to_dict_list(q.all(), exclude={"device_token_hash"})
