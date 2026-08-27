from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, HospitalProfile
from app.security import require_role
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/hospitals", tags=["hospitals"])


class HospitalProfileIn(BaseModel):
    hospital_name: str
    hospital_code: str
    phone: Optional[str] = None
    address: Optional[str] = None


@router.put("/me")
def upsert_my_profile(body: HospitalProfileIn, user: User = Depends(require_role("hospital")), db: Session = Depends(get_db)):
    profile = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
    if not profile:
        profile = HospitalProfile(user_id=user.id, hospital_name=body.hospital_name, hospital_code=body.hospital_code)
        db.add(profile)
    for field, value in body.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id, "verification_status": profile.verification_status}


@router.get("/me")
def get_my_profile(user: User = Depends(require_role("hospital")), db: Session = Depends(get_db)):
    profile = db.query(HospitalProfile).filter(HospitalProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No hospital profile yet — PUT /hospitals/me to create one.")
    return to_dict(profile)


@router.get("")
def list_hospitals(user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    return to_dict_list(db.query(HospitalProfile).all())
