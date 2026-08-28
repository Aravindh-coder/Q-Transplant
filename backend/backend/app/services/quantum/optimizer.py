"""Classical quantum-inspired optimizer for research benchmarking only."""
import random

def optimize(candidates: list[dict], score_fn, iterations: int | None = None, seed: int = 42) -> dict:
    rng=random.Random(seed)
    if not candidates: return {"best":None,"best_score":None,"evaluations":0}
    rounds=iterations or max(3, int(len(candidates) ** 0.5))
    weights=[1.0]*len(candidates); best=None; best_score=float('-inf'); evaluations=0
    sample=max(1, len(candidates)//rounds)
    for _ in range(rounds):
        indices=rng.choices(range(len(candidates)), weights=weights, k=sample)
        for i in set(indices):
            score=score_fn(candidates[i]); evaluations+=1
            if score>best_score: best,best_score=candidates[i],score
            weights[i] *= 1.05 + max(0.0, score)/(abs(best_score)+1.0)*0.05
    return {"best":best,"best_score":best_score,"evaluations":evaluations}
