from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DonorProfile
from app.security import get_current_user, require_role
from app.services.audit import log_action
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/donors", tags=["donors"])


class DonorProfileIn(BaseModel):
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    blood_group: str
    organs_available: list[str] = []
    hla_a: Optional[str] = None
    hla_b: Optional[str] = None
    hla_c: Optional[str] = None
    hla_dr: Optional[str] = None
    hla_dq: Optional[str] = None


@router.put("/me")
def upsert_my_profile(body: DonorProfileIn, user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        profile = DonorProfile(user_id=user.id, blood_group=body.blood_group)
        db.add(profile)
    for field, value in body.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    log_action(db, "DONOR_PROFILE_UPDATED", user_id=user.id)
    return {"id": profile.id, "verification_status": profile.verification_status}


@router.get("/me")
def get_my_profile(user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No donor profile yet — PUT /donors/me to create one.")
    return to_dict(profile)


@router.post("/me/availability")
def set_availability(active: bool, user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    profile = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(404, "No donor profile yet.")
    profile.availability_status = "active" if active else "inactive"
    db.commit()
    log_action(db, "DONOR_AVAILABILITY_CHANGED", user_id=user.id, target=profile.availability_status)
    return {"availability_status": profile.availability_status}


# doctors/hospitals search the donor pool — donors never see other donors
@router.get("/search")
def search_donors(organ: Optional[str] = None, blood_group: Optional[str] = None,
                   user: User = Depends(require_role("doctor", "hospital", "organizer")),
                   db: Session = Depends(get_db)):
    q = db.query(DonorProfile).filter(DonorProfile.availability_status == "active")
    if blood_group:
        q = q.filter(DonorProfile.blood_group == blood_group.upper())
    results = q.all()
    if organ:
        results = [d for d in results if any(o.replace("_partial", "") == organ.lower() for o in (d.organs_available or []))]
    return to_dict_list(results)
