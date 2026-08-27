import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Device, HospitalProfile
from app.security import require_role, hash_password
from app.services.audit import log_action
from app.routers.emergency import DEVICE_TOKEN_HASHES
from app.utils import to_dict_list

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.post("/provision")
def provision_device(hospital_id: str, firmware_version: str = "1.0.0",
                      user: User = Depends(require_role("organizer", "hospital")), db: Session = Depends(get_db)):
    """
    Generates a fresh device token for a hospital's ESP32 and returns it ONCE
    — only the hash is stored. Flash this token into the device firmware and
    discard it from wherever you copied it from.
    """
    hospital = db.query(HospitalProfile).filter(HospitalProfile.id == hospital_id).first()
    if not hospital:
        raise HTTPException(404, "Hospital not found.")

    raw_token = secrets.token_urlsafe(24)
    device = Device(hospital_id=hospital_id, device_token_hash=hash_password(raw_token),
                     firmware_version=firmware_version, connection_status="offline")
    db.add(device)
    db.commit()
    db.refresh(device)

    DEVICE_TOKEN_HASHES[hospital_id] = device.device_token_hash
    log_action(db, "DEVICE_PROVISIONED", user_id=user.id, target=hospital_id)

    return {"device_id": device.id, "device_token": raw_token,
            "warning": "This token is shown only once. Store it in the ESP32 firmware build now."}


@router.get("")
def list_devices(user: User = Depends(require_role("organizer", "hospital")), db: Session = Depends(get_db)):
    return to_dict_list(db.query(Device).all(), exclude={"device_token_hash"})
