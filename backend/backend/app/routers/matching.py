from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Patient, DonorProfile, MatchRequest, MatchResult, HospitalProfile, DoctorProfile
from app.security import require_role
from app.services.audit import log_action
from app.services.matching_engine import run_match
from app.services.clinical_safety import decision_support_payload
from app.services.ai_assistant import risk_flags, summarize_match, clinical_review
from app.services.match_workflow import workflow_plan
from app.services.notifications import notify, notify_organizer
from app.services.quantum.search import classical_search, quantum_inspired_search_traced
from app.utils import to_dict, to_dict_list

router = APIRouter(prefix="/api/v1/matching", tags=["matching"])

@router.get("/workflow")
def get_workflow_plan():
    """Public-shape description of the matching pipeline stages, for API
    documentation and frontend transparency (section 21/37 of the spec:
    every result should be explainable, including how it was produced)."""
    return workflow_plan()

def _donor_to_dict(d):
    return {"id":d.id,"blood_group":d.blood_group,"organs_available":d.organs_available or [],"availability_status":d.availability_status,"hla_a":d.hla_a,"hla_b":d.hla_b,"hla_c":d.hla_c,"hla_dr":d.hla_dr,"hla_dq":d.hla_dq}

def _patient_to_dict(p):
    return {"id":p.id,"blood_group":p.blood_group,"required_organ":p.required_organ,"urgency":p.urgency,"waiting_since":p.waiting_since,"eligible":True,"hla_a":p.hla_a,"hla_b":p.hla_b,"hla_c":p.hla_c,"hla_dr":p.hla_dr,"hla_dq":p.hla_dq}


class RecipientSearchIn(BaseModel):
    blood_group: str
    required_organ: str
    urgency: str = "MEDIUM"
    hla_a: Optional[str] = None
    hla_b: Optional[str] = None
    hla_c: Optional[str] = None
    hla_dr: Optional[str] = None
    hla_dq: Optional[str] = None
    ai_review_top_n: int = Field(3, ge=0, le=5, description="How many of the top matches get an AI clinical review (0 to skip entirely).")


@router.post("/search")
def search_by_criteria(body: RecipientSearchIn, user: User = Depends(require_role("doctor", "hospital", "organizer")), db: Session = Depends(get_db)):
    """Ad-hoc recipient search -- enter criteria directly, no saved Patient
    record required. Runs the same deterministic engine as /run/{patient_id},
    plus a traced quantum-inspired search (for the 'watch it search' demo
    view) and an AI clinical review on the top candidates. The deterministic
    ranking is what's authoritative; the traced search and AI review are
    both purely illustrative/assistive layers on top of it."""
    ad_hoc_patient = {
        "id": None, "blood_group": body.blood_group.upper(), "required_organ": body.required_organ.lower(),
        "urgency": body.urgency.upper(), "waiting_since": None, "eligible": True,
        "hla_a": body.hla_a, "hla_b": body.hla_b, "hla_c": body.hla_c, "hla_dr": body.hla_dr, "hla_dq": body.hla_dq,
    }
    donors = db.query(DonorProfile).filter(DonorProfile.availability_status == "active", DonorProfile.donation_status == "ACTIVE").all()
    donor_dicts = [_donor_to_dict(d) for d in donors]

    result = run_match(donor_dicts, ad_hoc_patient, top_n=len(donor_dicts) or 1)
    full_ranked = result["matches"]  # every candidate that passed blood+organ hard gates, fully scored
    result["matches"] = full_ranked[:10]
    result["matches"] = [{**m, **decision_support_payload(m)} for m in result["matches"]]
    for i, m in enumerate(result["matches"]):
        m["ai_assist"] = {"risk_flags": risk_flags(m), "summary": summarize_match(m)}
        if i < body.ai_review_top_n:
            m["ai_assist"]["clinical_review"] = clinical_review(m)

    # Traced quantum-inspired search over the SAME already-scored pool that
    # produced the deterministic ranking above -- for visualizing the
    # search process itself, not for deciding anything. Uses the FULL
    # ranked pool (every candidate that passed the hard gates), not just
    # the top 10 shown above, so the trace honestly reflects the real
    # search space instead of silently treating everyone outside the
    # display list as maximally incompatible.
    search_trace = None
    if len(donor_dicts) >= 3 and full_ranked:
        score_lookup = {m["donor_id"]: m["score"] for m in full_ranked}
        scoreable = [d for d in donor_dicts if d["id"] in score_lookup]
        classical = classical_search(scoreable, lambda d: score_lookup[d["id"]])
        traced = quantum_inspired_search_traced(scoreable, lambda d: score_lookup[d["id"]], lambda d: d["id"])
        search_trace = {
            "classical_evaluations": classical["evaluations"],
            "quantum_inspired_evaluations": traced["evaluations"],
            "iterations": traced["iterations"],
            "candidates_searched": traced["candidates_searched"],
            "steps": traced["trace"],
            "found_top_candidate": traced["best"]["id"] if traced["best"] else None,
            "matches_deterministic_top": (traced["best"]["id"] if traced["best"] else None) == (full_ranked[0]["donor_id"] if full_ranked else None),
        }

    log_action(db, "MATCH_SEARCH_AD_HOC", user_id=user.id, meta={"required_organ": body.required_organ, "candidates_evaluated": result["candidates_evaluated"], "matches_found": len(result["matches"])})
    return {"recipient_criteria": ad_hoc_patient, "candidates_evaluated": result["candidates_evaluated"],
            "matches": result["matches"], "quantum_comparison": result["quantum_comparison"], "search_trace": search_trace}


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
    for m in result["matches"]:
        # AI-assist layer: flags and phrasing only, never re-scores or
        # re-ranks -- the deterministic engine above has already decided.
        m["ai_assist"]={"risk_flags":risk_flags(m),"summary":summarize_match(m)}
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
