"""Transparent priority engine. Scores expose every factor used."""
from datetime import datetime, timezone

URGENCY_BASE = {"LOW": 10, "MEDIUM": 30, "HIGH": 55, "CRITICAL": 80, "EMERGENCY": 100}
MAX_WAIT_BONUS = 15
WAIT_DAYS_FOR_MAX_BONUS = 180
HOSPITAL_READINESS_BONUS = 5

def calculate_priority(urgency: str, waiting_since: datetime, hospital_ready: bool = True) -> dict:
    urgency = (urgency or "MEDIUM").upper()
    base = URGENCY_BASE.get(urgency, URGENCY_BASE["MEDIUM"])
    if waiting_since.tzinfo is None:
        waiting_since = waiting_since.replace(tzinfo=timezone.utc)
    days_waiting = max((datetime.now(timezone.utc) - waiting_since).days, 0)
    wait_bonus = min(MAX_WAIT_BONUS, round((days_waiting / WAIT_DAYS_FOR_MAX_BONUS) * MAX_WAIT_BONUS, 1))
    readiness_bonus = HOSPITAL_READINESS_BONUS if hospital_ready else 0
    return {"score": round(base + wait_bonus + readiness_bonus, 1), "factors": {
        "urgency": urgency, "urgency_base_points": base, "days_waiting": days_waiting,
        "wait_bonus_points": wait_bonus, "hospital_ready": hospital_ready,
        "readiness_bonus_points": readiness_bonus}}

def calculate_recipient_priority(recipient: dict, hospital_ready: bool = True) -> dict:
    waiting_since = recipient.get("waiting_since")
    if isinstance(waiting_since, str):
        try: waiting_since = datetime.fromisoformat(waiting_since.replace("Z", "+00:00"))
        except ValueError: waiting_since = None
    if not isinstance(waiting_since, datetime): waiting_since = datetime.now(timezone.utc)
    return calculate_priority(recipient.get("urgency", "MEDIUM"), waiting_since, hospital_ready)
