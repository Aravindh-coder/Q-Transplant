"""Deterministic organ compatibility."""
from app.services.compatibility import check_organ_compatibility

def check_organ(donor: dict, recipient: dict, hospital_ready: bool = True) -> dict:
    required = recipient.get("required_organ", "").lower()
    available = next((str(o).lower().replace("_partial", "") for o in donor.get("organs_available", []) if str(o).lower().replace("_partial", "") == required), None)
    return check_organ_compatibility(required, available or "", donor.get("availability_status", "").lower() == "active", recipient.get("eligible", True) and hospital_ready)
