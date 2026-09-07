from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DonorProfile, Patient, DoctorProfile, DonorRequest, Notification
from app.security import require_role
from app.services.audit import log_action
from app.services.mailer import send_email

router = APIRouter(prefix="/api/v1/donor-requests", tags=["donor requests"])


class CreateRequestIn(BaseModel):
    donor_id: str
    organ: str
    urgency: str = "MEDIUM"
    patient_id: Optional[str] = None
    message: Optional[str] = None


class RespondIn(BaseModel):
    decision: str


class CancelIn(BaseModel):
    reason: Optional[str] = None


def _request_view(req: DonorRequest, requester: User, donor: DonorProfile):
    return {"id": req.id, "organ": req.organ, "urgency": req.urgency, "message": req.message,
            "status": req.status, "created_at": req.created_at, "responded_at": req.responded_at,
            "requested_by": {"name": requester.full_name or requester.email, "role": requester.role},
            "donor_id": donor.id}


@router.post("")
def create_request(body: CreateRequestIn, user: User = Depends(require_role("doctor", "hospital")), db: Session = Depends(get_db)):
    donor = db.query(DonorProfile).filter(DonorProfile.id == body.donor_id).first()
    if not donor:
        raise HTTPException(404, "Donor not found.")
    if donor.availability_status != "active":
        raise HTTPException(409, "Donor is currently inactive and cannot receive a new request.")
    if donor.verification_status != "verified":
        raise HTTPException(409, "Donor has not been verified yet and cannot receive a new request.")
    if not body.organ.strip():
        raise HTTPException(400, "organ is required")
    urgency = body.urgency.upper()
    if urgency not in {"LOW", "MEDIUM", "HIGH", "CRITICAL", "EMERGENCY"}:
        raise HTTPException(400, "Invalid urgency level.")
    if body.patient_id:
        patient = db.query(Patient).filter(Patient.id == body.patient_id).first()
        if not patient:
            raise HTTPException(404, "Patient not found.")
        if user.role == "doctor":
            dp = db.query(DoctorProfile).filter(DoctorProfile.user_id == user.id).first()
            if dp and patient.doctor_id != dp.id:
                raise HTTPException(403, "You can only request a donor for your own patient case.")

    req = DonorRequest(donor_id=donor.id, patient_id=body.patient_id, requested_by=user.id,
                       organ=body.organ.strip(), urgency=urgency, message=body.message, status="pending")
    db.add(req)
    db.flush()
    db.add(Notification(recipient_user_id=donor.user_id, type="IN_APP",
                         title=f"New {req.organ} donation request",
                         message=(f"{user.full_name or user.email} ({user.role}) sent you a {urgency} "
                                  "donation request. Open your donor requests to respond."),
                         priority="critical" if urgency in {"CRITICAL", "EMERGENCY"} else "high"))
    db.commit()
    db.refresh(req)

    donor_user = db.query(User).filter(User.id == donor.user_id).first()
    if donor_user:
        try:
            send_email(donor_user.email, f"Q-Transplant — {urgency} donor request",
                       f"You have a new {req.organ} donation request from {user.full_name or user.email} ({user.role}). "
                       "Log in to Q-Transplant to review and respond.")
        except RuntimeError:
            pass
    log_action(db, "DONOR_REQUEST_CREATED", user_id=user.id, target=req.id,
               meta={"donor_id": donor.id, "urgency": urgency, "organ": req.organ})
    return _request_view(req, user, donor)


@router.get("/me")
def my_requests(user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    donor = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    if not donor:
        raise HTTPException(404, "Donor profile not found.")
    rows = (db.query(DonorRequest, User).join(User, User.id == DonorRequest.requested_by)
            .filter(DonorRequest.donor_id == donor.id).order_by(DonorRequest.created_at.desc()).all())
    return [_request_view(req, requester, donor) for req, requester in rows]


@router.get("/{request_id}")
def get_request(request_id: str, user: User = Depends(require_role("donor", "doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    req = db.query(DonorRequest).filter(DonorRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found.")
    if user.role == "donor":
        donor = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
        if not donor or req.donor_id != donor.id:
            raise HTTPException(403, "Not authorized to view this request.")
    elif user.role in {"doctor", "hospital"} and req.requested_by != user.id:
        raise HTTPException(403, "Not authorized to view this request.")
    donor = db.query(DonorProfile).filter(DonorProfile.id == req.donor_id).first()
    requester = db.query(User).filter(User.id == req.requested_by).first()
    return _request_view(req, requester, donor)


@router.post("/{request_id}/respond")
def respond(request_id: str, body: RespondIn, user: User = Depends(require_role("donor")), db: Session = Depends(get_db)):
    decision = body.decision.lower()
    if decision not in {"accepted", "declined"}:
        raise HTTPException(400, "decision must be accepted or declined")
    donor = db.query(DonorProfile).filter(DonorProfile.user_id == user.id).first()
    req = db.query(DonorRequest).filter(DonorRequest.id == request_id).first()
    if not donor or not req or req.donor_id != donor.id:
        raise HTTPException(404, "Request not found.")
    if req.status != "pending":
        raise HTTPException(409, "This request has already been answered.")
    req.status = decision
    req.responded_at = datetime.now(timezone.utc)
    if decision == "accepted":
        donor.donation_status = "MATCHED"
    db.add(Notification(recipient_user_id=req.requested_by, type="IN_APP",
                         title=f"Donor request {decision}",
                         message=f"The donor has {decision} your {req.organ} request.", priority="high"))
    db.commit()
    requester = db.query(User).filter(User.id == req.requested_by).first()
    if requester:
        try:
            send_email(requester.email, f"Q-Transplant — donor request {decision}",
                       f"The donor has {decision} your {req.organ} request.")
        except RuntimeError:
            pass
    log_action(db, "DONOR_REQUEST_RESPONDED", user_id=user.id, target=req.id, meta={"decision": decision})
    return {"request_id": req.id, "status": req.status, "donation_status": donor.donation_status}


@router.post("/{request_id}/cancel")
def cancel(request_id: str, body: CancelIn, user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    req = db.query(DonorRequest).filter(DonorRequest.id == request_id).first()
    if not req:
        raise HTTPException(404, "Request not found.")
    if user.role != "organizer" and req.requested_by != user.id:
        raise HTTPException(403, "Not authorized to cancel this request.")
    if req.status != "pending":
        raise HTTPException(409, "Only pending requests can be cancelled.")
    req.status = "cancelled"
    donor = db.query(DonorProfile).filter(DonorProfile.id == req.donor_id).first()
    if donor:
        db.add(Notification(recipient_user_id=donor.user_id, type="IN_APP", title="Donation request cancelled",
                             message=body.reason or "A medical personnel request was cancelled.", priority="normal"))
    db.commit()
    log_action(db, "DONOR_REQUEST_CANCELLED", user_id=user.id, target=req.id)
    return {"request_id": req.id, "status": req.status}
