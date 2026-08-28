"""Deterministic blood compatibility adapter."""
from app.services.compatibility import check_blood_compatibility

def check_blood(donor: dict, recipient: dict) -> dict:
    return check_blood_compatibility(donor.get("blood_group"), recipient.get("blood_group"))
