"""Clinical decision-support boundary for all matching outputs."""
DISCLAIMER = "Q-Transplant provides compatibility information, ranking and warnings for qualified professionals; it does not independently determine whether a transplant is medically safe."

def decision_support_payload(result: dict) -> dict:
    return {"compatibility": result.get("compatibility", {}), "ranking": result.get("score"), "explanation": result.get("explanation"), "warnings": result.get("warnings", []), "clinical_decision_required": True, "disclaimer": DISCLAIMER}
