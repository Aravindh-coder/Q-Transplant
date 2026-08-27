"""
Transparent priority engine. Every score ships with the factors that
produced it — no opaque ranking. Weights are configurable constants,
documented here, not hidden inside a model.
"""
from datetime import datetime, timezone

URGENCY_BASE = {
    "LOW": 10,
    "MEDIUM": 30,
    "HIGH": 55,
    "CRITICAL": 80,
    "EMERGENCY": 100,
}

MAX_WAIT_BONUS = 15       # points added for very long waits, capped
WAIT_DAYS_FOR_MAX_BONUS = 180
HOSPITAL_READINESS_BONUS = 5


def calculate_priority(urgency: str, waiting_since: datetime, hospital_ready: bool = True) -> dict:
    """
    Returns {"score": float, "factors": {...}} so the UI can always show why
    a recipient was ranked where it was.
    """
    urgency = (urgency or "MEDIUM").upper()
    base = URGENCY_BASE.get(urgency, URGENCY_BASE["MEDIUM"])

    if waiting_since.tzinfo is None:
        waiting_since = waiting_since.replace(tzinfo=timezone.utc)
    days_waiting = max((datetime.now(timezone.utc) - waiting_since).days, 0)
    wait_bonus = min(MAX_WAIT_BONUS, round((days_waiting / WAIT_DAYS_FOR_MAX_BONUS) * MAX_WAIT_BONUS, 1))

    readiness_bonus = HOSPITAL_READINESS_BONUS if hospital_ready else 0

    score = round(base + wait_bonus + readiness_bonus, 1)
    return {
        "score": score,
        "factors": {
            "urgency": urgency,
            "urgency_base_points": base,
            "days_waiting": days_waiting,
            "wait_bonus_points": wait_bonus,
            "hospital_ready": hospital_ready,
            "readiness_bonus_points": readiness_bonus,
        },
    }
