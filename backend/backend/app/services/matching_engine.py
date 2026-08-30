"""
Matching engine pipeline:
  patient -> filter by organ -> eligibility -> blood compatibility -> HLA
  -> urgency -> availability -> ranking -> top candidates

Deterministic rules run first and are never overridden by AI. The optional
`ai_explain` hook is where an LLM call (Groq/Gemini/Claude) can turn the
structured result into a natural-language summary for a doctor — it only
rephrases what the deterministic engine already decided, never re-decides.
"""
from typing import Callable, Optional

from app.services.compatibility import check_blood_compatibility, check_organ_compatibility
from app.services.hla import calculate_hla_match
from app.services.urgency import calculate_priority
from app.services.quantum.search import classical_search, quantum_inspired_search

# Score weighting — documented, not hidden. Blood/organ are hard gates (0 or
# fail the candidate entirely); HLA and urgency combine into the ranking score.
HLA_WEIGHT = 0.7
URGENCY_WEIGHT = 0.3


def evaluate_candidate(donor: dict, patient: dict, hospital_ready: bool = True) -> Optional[dict]:
    """
    donor: {"id","blood_group","organs_available":[...], "availability_status", hla_a..hla_dq}
    patient: {"id","blood_group","required_organ","urgency","waiting_since", hla_a..hla_dq, "eligible"}
    Returns None if the candidate fails a hard gate (blood/organ), otherwise
    a full explained result.
    """
    blood = check_blood_compatibility(donor["blood_group"], patient["blood_group"])
    if not blood["compatible"]:
        return None

    donor_available = str(donor.get("availability_status", "active")).lower() == "active"
    recipient_eligible = patient.get("eligible", True)
    required_organ = str(patient["required_organ"]).lower()
    organ_available = next(
        (o for o in donor.get("organs_available", []) if str(o).lower().replace("_partial", "") == required_organ),
        None,
    )
    organ = check_organ_compatibility(
        patient["required_organ"], organ_available or patient["required_organ"],
        donor_available and organ_available is not None, recipient_eligible,
    )
    if not organ["compatible"]:
        return None

    hla = calculate_hla_match(donor, patient)
    priority = calculate_priority(patient.get("urgency", "MEDIUM"), patient.get("waiting_since"), hospital_ready)

    # normalize urgency score (0-100 range roughly) for blending with HLA %
    urgency_normalized = min(100, priority["score"])
    overall = round(hla["score"] * HLA_WEIGHT + urgency_normalized * URGENCY_WEIGHT, 1)

    return {
        "donor_id": donor["id"],
        "score": overall,
        "blood_compatible": True,
        "blood_reason": blood["reason"],
        "organ_compatible": True,
        "hla_score": hla["score"],
        "hla_details": hla["details"],
        "urgency": patient.get("urgency", "MEDIUM"),
        "priority_factors": priority["factors"],
        "explanation": (
            f"Blood compatibility: PASS. Organ compatibility: PASS. "
            f"HLA compatibility: {hla['score']}%. Recipient urgency: {patient.get('urgency','MEDIUM')}. "
            f"Overall ranking: {overall}/100."
        ),
    }


def run_match(donors: list[dict], patient: dict, hospital_ready: bool = True,
              ai_explain: Optional[Callable[[dict], str]] = None, top_n: int = 5) -> dict:
    """
    Runs the full pipeline over a candidate donor pool for one patient and
    returns the ranked top_n. Pass `ai_explain` (a function taking the result
    dict and returning a string) to attach an AI-generated natural-language
    summary on top of the deterministic explanation — never in place of it.
    """
    results = []
    for donor in donors:
        r = evaluate_candidate(donor, patient, hospital_ready)
        if r:
            results.append(r)

    results.sort(key=lambda r: r["score"], reverse=True)
    top = results[:top_n]
    for i, r in enumerate(top, start=1):
        r["rank"] = i
        if ai_explain:
            try:
                r["ai_summary"] = ai_explain(r)
            except Exception:
                r["ai_summary"] = None  # AI layer failing never blocks the deterministic result

    quantum_comparison = None
    if results:
        # Search-performance comparison only -- classical/quantum-inspired
        # both search over the SAME already-scored pool, never re-scoring
        # or re-ranking. Reported honestly per the module's own docstring:
        # this is a classical amplitude-amplification-style heuristic, not
        # real quantum hardware, and isn't guaranteed to find the true
        # optimum the way the exhaustive scan above already has.
        score_fn = lambda r: r["score"]
        classical = classical_search(results, score_fn)
        quantum = quantum_inspired_search(results, score_fn)
        quantum_comparison = {
            "candidates_searched": len(results),
            "classical_evaluations": classical["evaluations"],
            "quantum_inspired_evaluations": quantum["evaluations"],
            "quantum_found_same_top_candidate": (quantum["best"] or {}).get("donor_id") == (top[0]["donor_id"] if top else None),
            "note": "Comparison only -- the ranking above is the deterministic classical result and is authoritative regardless of what this shows.",
        }

    return {"patient_id": patient["id"], "candidates_evaluated": len(donors), "matches": top, "quantum_comparison": quantum_comparison}
