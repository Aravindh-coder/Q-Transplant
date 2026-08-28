"""Transparent candidate ranking. Weights are explicit and configurable."""
HLA_WEIGHT = 0.70
URGENCY_WEIGHT = 0.30

def rank_candidate(hla_score: float, priority_score: float, factors: list[dict]) -> dict:
    score = round(max(0.0, min(100.0, hla_score)) * HLA_WEIGHT + max(0.0, min(100.0, priority_score)) * URGENCY_WEIGHT, 2)
    explanation = "HLA contributes 70%; urgency/priority contributes 30%. " + " ".join(f.get("reason", "") for f in factors if f.get("reason"))
    return {"score": score, "weights": {"hla": HLA_WEIGHT, "urgency": URGENCY_WEIGHT}, "explanation": explanation.strip()}

def rank_candidates(candidates: list[dict]) -> list[dict]:
    ranked = sorted(candidates, key=lambda x: x.get("score", 0), reverse=True)
    for i, item in enumerate(ranked, 1):
        item["rank"] = i
    return ranked
