from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DoctorProfile, HospitalProfile
from app.security import get_current_user, require_role
from app.services.audit import log_action
from app.services.notifications import notify
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/doctors", tags=["doctors"])


class DoctorProfileIn(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    license_number: str
    specialty: Optional[str] = None
    hospital_id: Optional[str] = None


@router.put("/me")
def upsert_my_profile(body: DoctorProfileIn, user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
    if not profile:
        profile = DoctorProfile(user_id=user.id, license_number=body.license_number)
        db.add(profile)
    for field, value in body.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id, "approval_status": profile.approval_status}


@router.get("/me")
def get_my_profile(user: User = Depends(require_role("doctor")), db: Session = Depends(get_db)):
    profile = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No doctor profile yet — PUT /doctors/me to create one.")
    return to_dict(profile)


@router.get("")
def list_doctors(hospital_id: Optional[str] = None,
                  user: User = Depends(require_role("hospital", "organizer")),
                  db: Session = Depends(get_db)):
    q = db.query(DoctorProfile)
    if hospital_id:
        q = q.filter(DoctorProfile.hospital_id == hospital_id)
    return to_dict_list(q.all())
