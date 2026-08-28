"""Validated emergency lifecycle and audit helpers."""
from datetime import datetime, timezone

EMERGENCY_STATUSES = ("CREATED", "NOTIFIED", "ACKNOWLEDGED", "PROCESSING", "RESOLVED", "CANCELLED")
TRANSITIONS = {
    "CREATED": {"NOTIFIED", "CANCELLED"},
    "NOTIFIED": {"ACKNOWLEDGED", "CANCELLED"},
    "ACKNOWLEDGED": {"PROCESSING", "CANCELLED"},
    "PROCESSING": {"RESOLVED", "CANCELLED"},
    "RESOLVED": set(),
    "CANCELLED": set(),
}

def transition(current: str, new: str) -> str:
    current = current.upper(); new = new.upper()
    if current not in EMERGENCY_STATUSES or new not in TRANSITIONS.get(current, set()):
        raise ValueError(f"Invalid emergency transition: {current} -> {new}")
    return new

def timestamp():
    return datetime.now(timezone.utc)
