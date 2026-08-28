"""Transparent urgency/priority adapter."""
from app.services.urgency import calculate_priority

def calculate_recipient_priority(recipient: dict, hospital_ready: bool = True) -> dict:
    return calculate_priority(recipient.get("urgency", "MEDIUM"), recipient.get("waiting_since"), hospital_ready)
