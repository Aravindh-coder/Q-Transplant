from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DoctorProfile, HospitalProfile
from app.security import get_current_user, require_role
from app.services.audit import log_action
from app.services.notifications import notify
from app.services.search_service import paginate
from app.services.performance import bounded_page, DEFAULT_PAGE_SIZE
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
    for field, value in body.model_dump(exclude_unset=True).items():
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
def list_doctors(hospital_id: Optional[str] = None, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE,
                  user: User = Depends(require_role("hospital", "organizer")),
                  db: Session = Depends(get_db)):
    page, page_size = bounded_page(page, page_size)
    q = db.query(DoctorProfile)
    if hospital_id:
        q = q.filter(DoctorProfile.hospital_id == hospital_id)
    paginated = paginate(q, page, page_size)
    return {**paginated, "items": to_dict_list(paginated["items"])}
