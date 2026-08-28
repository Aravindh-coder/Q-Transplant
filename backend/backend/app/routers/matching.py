from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Patient, DonorProfile, MatchRequest, MatchResult, HospitalProfile, DoctorProfile
from app.security import require_role
from app.services.audit import log_action
from app.services.matching_engine import run_match
from app.services.clinical_safety import decision_support_payload
from app.services.notifications import notify, notify_organizer
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/matching", tags=["matching"])

def _donor_to_dict(d):
    return {"id":d.id,"blood_group":d.blood_group,"organs_available":d.organs_available or [],"availability_status":d.availability_status,"hla_a":d.hla_a,"hla_b":d.hla_b,"hla_c":d.hla_c,"hla_dr":d.hla_dr,"hla_dq":d.hla_dq}

def _patient_to_dict(p):
    return {"id":p.id,"blood_group":p.blood_group,"required_organ":p.required_organ,"urgency":p.urgency,"waiting_since":p.waiting_since,"eligible":True,"hla_a":p.hla_a,"hla_b":p.hla_b,"hla_c":p.hla_c,"hla_dr":p.hla_dr,"hla_dq":p.hla_dq}

@router.post("/run/{patient_id}")
def run_match_for_patient(patient_id: str, user: User = Depends(require_role("doctor","hospital")), db: Session = Depends(get_db)):
    patient=db.query(Patient).filter(Patient.id==patient_id).first()
    if not patient: raise HTTPException(404,"Patient not found.")
    if user.role=="doctor":
        doctor=db.query(DoctorProfile).filter(DoctorProfile.user_id==user.id).first()
        if not doctor or doctor.hospital_id!=patient.hospital_id: raise HTTPException(403,"You are not authorized for this patient.")
    else:
        hospital=db.query(HospitalProfile).filter(HospitalProfile.user_id==user.id).first()
        if not hospital or hospital.id!=patient.hospital_id: raise HTTPException(403,"You are not authorized for this patient.")
    donors=db.query(DonorProfile).filter(DonorProfile.availability_status=="active",DonorProfile.donation_status=="ACTIVE").all()
    result=run_match([_donor_to_dict(d) for d in donors],_patient_to_dict(patient))
    result["matches"]=[{**m,**decision_support_payload(m)} for m in result["matches"]]
    req=MatchRequest(patient_id=patient.id,requested_by=user.id,organ=patient.required_organ,status="completed"); db.add(req); db.flush()
    for m in result["matches"]:
        db.add(MatchResult(match_request_id=req.id,donor_id=m["donor_id"],blood_compatible=m["blood_compatible"],hla_score=m["hla_score"],organ_compatible=m["organ_compatible"],urgency_at_match=m["urgency"],overall_score=m["score"],explanation=m,rank=m["rank"]))
    notify(db,user,"Match analysis completed",f"{len(result['matches'])} compatible donor candidate(s) were ranked for patient {patient.id}.","normal",True)
    db.commit()
    notify_organizer("Q-Transplant — match found",f"A compatibility analysis found {len(result['matches'])} candidate(s) for patient {patient.id}.")
    log_action(db,"MATCH_GENERATED",user_id=user.id,target=patient_id,meta={"candidates_evaluated":result["candidates_evaluated"],"matches_found":len(result["matches"])})
    return {"match_request_id":req.id,**result}

@router.get("/history/{patient_id}")
def match_history(patient_id: str,user: User=Depends(require_role("doctor","hospital","organizer")),db:Session=Depends(get_db)):
    requests=db.query(MatchRequest).filter(MatchRequest.patient_id==patient_id).all(); out=[]
    for r in requests:
        results=db.query(MatchResult).filter(MatchResult.match_request_id==r.id).order_by(MatchResult.rank).all(); out.append({"request":to_dict(r),"results":to_dict_list(results)})
    return out
