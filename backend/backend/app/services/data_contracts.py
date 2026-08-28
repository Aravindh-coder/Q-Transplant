"""Roadmap data contracts and privacy-safe serializers for Q-Transplant."""
from datetime import datetime

SUPPORTED_ORGANS = ("kidney", "liver", "heart", "lung", "pancreas", "intestine")

DONOR_FIELDS = (
    "id", "name", "email", "phone", "date_of_birth", "age", "gender", "address",
    "blood_group", "organs_available", "medical_status", "hla_a", "hla_b", "hla_c",
    "hla_dr", "hla_dq", "availability_status", "hospital_id", "verification_status",
    "created_at", "updated_at",
)
PATIENT_FIELDS = (
    "id", "name", "age", "gender", "blood_group", "required_organ", "hla_a", "hla_b",
    "hla_c", "hla_dr", "hla_dq", "urgency", "hospital_id", "doctor_id", "waiting_status",
    "medical_compatibility", "priority_score", "created_at", "updated_at",
)


def calculate_age(date_of_birth):
    if not date_of_birth:
        return None
    today = datetime.utcnow().date()
    return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))


def serialize_donor(donor, include_private=False):
    """Return only fields appropriate to the caller; never expose secrets."""
    result = {k: getattr(donor, k, None) for k in DONOR_FIELDS if hasattr(donor, k)}
    dob = getattr(donor, "date_of_birth", None)
    result["age"] = calculate_age(dob)
    if not include_private:
        for key in ("email", "phone", "address", "date_of_birth"):
            result.pop(key, None)
    return result


def serialize_patient(patient, include_private=False):
    result = {k: getattr(patient, k, None) for k in PATIENT_FIELDS if hasattr(patient, k)}
    if not include_private:
        result.pop("name", None)
    return result
