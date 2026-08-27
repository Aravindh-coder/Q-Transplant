"""
Deterministic blood-group and organ compatibility rules.
No AI model touches this file — medical compatibility is never invented by
a language model. Every function here is pure and independently testable.
"""

# Standard donor -> compatible recipient blood groups
BLOOD_COMPATIBILITY = {
    "O-": {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"},  # universal donor
    "O+": {"O+", "A+", "B+", "AB+"},
    "A-": {"A-", "A+", "AB-", "AB+"},
    "A+": {"A+", "AB+"},
    "B-": {"B-", "B+", "AB-", "AB+"},
    "B+": {"B+", "AB+"},
    "AB-": {"AB-", "AB+"},
    "AB+": {"AB+"},  # universal recipient, but donates only to AB+
}

VALID_ORGANS = {"kidney", "liver", "heart", "lung", "pancreas", "intestine"}


def check_blood_compatibility(donor_blood_group: str, recipient_blood_group: str) -> dict:
    """
    check_blood_compatibility(donor, recipient) -> {"compatible": bool, "reason": str}
    """
    donor_blood_group = (donor_blood_group or "").upper()
    recipient_blood_group = (recipient_blood_group or "").upper()

    if donor_blood_group not in BLOOD_COMPATIBILITY:
        return {"compatible": False, "reason": f"Unknown donor blood group '{donor_blood_group}'."}
    if recipient_blood_group not in BLOOD_COMPATIBILITY:
        return {"compatible": False, "reason": f"Unknown recipient blood group '{recipient_blood_group}'."}

    compatible = recipient_blood_group in BLOOD_COMPATIBILITY[donor_blood_group]
    reason = (
        f"{donor_blood_group} donor is compatible with {recipient_blood_group} recipient."
        if compatible else
        f"{donor_blood_group} donor is NOT compatible with {recipient_blood_group} recipient."
    )
    return {"compatible": compatible, "reason": reason}


def check_organ_compatibility(required_organ: str, available_organ: str,
                               donor_available: bool, recipient_eligible: bool) -> dict:
    """
    check_organ_compatibility() -> {"compatible": bool, "reason": str}
    Checks organ type match plus the two eligibility flags the caller has
    already determined from donor/recipient records (availability status,
    medical eligibility).
    """
    required_organ = (required_organ or "").lower()
    available_organ = (available_organ or "").lower().replace("_partial", "")

    if required_organ not in VALID_ORGANS:
        return {"compatible": False, "reason": f"'{required_organ}' is not a supported organ type."}
    if required_organ != available_organ:
        return {"compatible": False, "reason": f"Recipient needs {required_organ}, donor organ is {available_organ}."}
    if not donor_available:
        return {"compatible": False, "reason": "Donor is not currently marked available."}
    if not recipient_eligible:
        return {"compatible": False, "reason": "Recipient does not currently meet medical eligibility criteria."}

    return {"compatible": True, "reason": f"Organ type matches ({required_organ}); donor and recipient both eligible."}
