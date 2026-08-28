"""Non-authoritative AI assistance utilities.
All medical compatibility decisions must be made by deterministic services first.
"""
from collections import Counter

def explain_match(match: dict) -> str:
    return match.get("explanation", "Deterministic compatibility analysis completed.")

def detect_data_quality(record: dict) -> list[str]:
    issues=[]
    required=("blood_group","required_organ")
    for field in required:
        if not record.get(field): issues.append(f"Missing required field: {field}")
    if record.get("age") is not None and not 0 <= record["age"] <= 120: issues.append("Age is outside the expected range.")
    return issues

def detect_duplicates(records: list[dict], keys=("email",)) -> list[dict]:
    groups={}
    for r in records:
        key=tuple(r.get(k) for k in keys)
        if all(v for v in key): groups.setdefault(key, []).append(r)
    return [v for v in groups.values() if len(v)>1]

def risk_flags(match: dict) -> list[str]:
    flags=[]
    if match.get("hla_score", 0) < 50: flags.append("Lower HLA similarity; clinician review required.")
    if match.get("priority_score", 0) >= 90: flags.append("High-priority recipient; coordinate urgently.")
    return flags

def summarize_match(match: dict) -> str:
    return f"Rank {match.get('rank','-')}, score {match.get('score',0)}; blood compatibility passed; HLA score {match.get('hla_score',0)}; urgency {match.get('urgency','UNKNOWN')}."

def search_assist(query: str, records: list[dict]) -> list[dict]:
    q=(query or "").strip().lower()
    if not q: return []
    return [r for r in records if q in " ".join(str(v) for v in r.values()).lower()]
