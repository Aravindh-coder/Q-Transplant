"""Full deterministic matching pipeline -- delegates to the canonical,
live implementation in app.services.matching_engine (used by the actual
/api/v1/matching/run/{patient_id} endpoint) rather than maintaining a
second, parallel copy of the same logic.

This module (and its siblings blood.py/hla.py/organ.py/urgency.py/
ranking.py in this package) used to be a fully separate implementation
that nothing in the live app actually called -- only unit tests exercised
it, so a bug fixed in the real pipeline could silently stay broken here
and vice versa. That's genuinely risky for a medical matching system, so
this now re-exports the real thing under the interface this package's
tests already expect.
"""
from app.services.matching_engine import evaluate_candidate, run_match


def evaluate(donor: dict, recipient: dict, hospital_ready: bool = True) -> dict | None:
    return evaluate_candidate(donor, recipient, hospital_ready)


def run_matching(donors: list[dict], recipient: dict, hospital_ready: bool = True, top_n: int = 5) -> dict:
    result = run_match(donors, recipient, hospital_ready, top_n=top_n)
    return {"patient_id": result["patient_id"], "candidates_evaluated": result["candidates_evaluated"], "matches": result["matches"]}
