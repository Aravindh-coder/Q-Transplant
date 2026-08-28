"""Clinical safety boundaries for the decision-support platform."""
MEDICAL_DISCLAIMER = (
    "Q-Transplant is a technology and clinical decision-support platform. "
    "Compatibility scores and rankings do not independently determine medical safety. "
    "Final clinical decisions remain with qualified medical professionals and applicable authorities."
)

def decision_support_payload(data: dict) -> dict:
    result = dict(data)
    result["clinical_decision"] = None
    result["disclaimer"] = MEDICAL_DISCLAIMER
    return result
