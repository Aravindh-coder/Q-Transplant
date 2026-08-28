"""Transparent candidate ranking. Weights are explicit and configurable."""
HLA_WEIGHT = 0.70
URGENCY_WEIGHT = 0.30

def rank_candidate(hla_score: float, priority_score: float, factors=None) -> dict:
    score = round(max(0.0, min(100.0, hla_score)) * HLA_WEIGHT + max(0.0, min(100.0, priority_score)) * URGENCY_WEIGHT, 2)
    reasons = []
    if isinstance(factors, dict):
        reasons.append(f"Urgency={factors.get('urgency', 'UNKNOWN')}")
        reasons.append(f"waiting bonus={factors.get('wait_bonus_points', 0)}")
        reasons.append(f"hospital readiness bonus={factors.get('readiness_bonus_points', 0)}")
    elif isinstance(factors, list):
        reasons.extend(str(f.get("reason", "")) for f in factors if isinstance(f, dict) and f.get("reason"))
    explanation = "HLA contributes 70%; urgency/priority contributes 30%. " + " ".join(reasons)
    return {"score": score, "weights": {"hla": HLA_WEIGHT, "urgency": URGENCY_WEIGHT}, "explanation": explanation.strip()}

def rank_candidates(candidates: list[dict]) -> list[dict]:
    ranked = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
    for i, item in enumerate(ranked, 1): item["rank"] = i
    return ranked
