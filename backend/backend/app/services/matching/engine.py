"""Full deterministic matching pipeline; AI is optional and cannot override gates."""
from .blood import check_blood
from .hla import check_hla
from .organ import check_organ
from .urgency import calculate_recipient_priority
from .ranking import rank_candidate

def evaluate(donor: dict, recipient: dict, hospital_ready: bool = True) -> dict | None:
    blood = check_blood(donor, recipient)
    if not blood["compatible"]:
        return None
    organ = check_organ(donor, recipient, hospital_ready)
    if not organ["compatible"]:
        return None
    hla = check_hla(donor, recipient)
    priority = calculate_recipient_priority(recipient, hospital_ready)
    ranked = rank_candidate(hla.get("score", 0), priority.get("score", 0), priority.get("factors", []))
    return {"donor_id": donor.get("id"), "blood_compatible": True, "blood_reason": blood["reason"], "organ_compatible": True, "hla_score": hla.get("score", 0), "hla_details": hla.get("details", {}), "urgency": recipient.get("urgency", "MEDIUM"), "priority_score": priority.get("score", 0), "priority_factors": priority.get("factors", []), **ranked}

def run_matching(donors: list[dict], recipient: dict, hospital_ready: bool = True, top_n: int = 5) -> dict:
    matches = [r for d in donors if (r := evaluate(d, recipient, hospital_ready)) is not None]
    matches = rank_candidates(matches)
    for r in matches:
        r["explanation"] = (r.get("explanation", "") + f" Deterministic gates passed: blood, organ, HLA evaluation, urgency and availability. Candidate rank: {r['rank']}.").strip()
    return {"patient_id": recipient.get("id"), "candidates_evaluated": len(donors), "matches": matches[:max(1, top_n)]}
