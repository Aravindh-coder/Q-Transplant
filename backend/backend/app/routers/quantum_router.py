from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DonorProfile, User
from app.security import require_role
from app.services.quantum.search import classical_search, quantum_inspired_search
from app.services.quantum.benchmark import run_benchmark
from app.services.quantum.grover_sim import simulate_grover_steps

router = APIRouter(prefix="/api/v1/quantum", tags=["quantum"])

@router.get("/grover-sim")
def get_grover_simulation(n_candidates: int = Query(64, ge=4, le=1000), target_index: int = Query(3, ge=0)):
    import math
    optimal_iters = max(1, int(round((math.pi / 4.0) * math.sqrt(n_candidates))))
    return {
        "n_candidates": n_candidates,
        "target_index": target_index,
        "theoretical_optimal_iterations": optimal_iters,
        "steps": simulate_grover_steps(n_candidates, target_index, max_steps=optimal_iters)
    }

@router.get("/benchmark")
def get_quantum_benchmark():
    import math, random as rng
    results = []
    for n in [10, 100, 500, 1000]:
        cands = [{"id": i, "score": rng.random()} for i in range(n)]
        def sf(c): return c["score"]
        from app.services.quantum.benchmark import run_benchmark
        r = run_benchmark(cands, sf)
        results.append({
            "pool_size": n,
            "classical_evals": r["classical"]["evaluations"],
            "quantum_evals": r["quantum_inspired"]["evaluations"],
            "reduction_pct": r["evaluation_reduction_pct"],
            "classical_time_s": r["classical"]["time_seconds"],
            "quantum_time_s": r["quantum_inspired"]["time_seconds"],
            "theoretical_speedup": f"{n / max(1, int(math.sqrt(n))):.1f}x",
            "same_optimum": r["same_optimum_found"]
        })
    return {"benchmark": results}

@router.get("/search-donors")
def search_donors_quantum(organ: str, blood_group: str,
                           user: User = Depends(require_role("doctor", "hospital", "organizer")),
                           db: Session = Depends(get_db)):
    """Was previously unauthenticated and returned donor IDs, blood groups,
    and organ availability for every active donor to anyone -- brought in
    line with every other donor-data endpoint (donors.py /search,
    matching.py /search), which all require an authorized clinical role.
    HLA fields are fetched for scoring context only and are never included
    in the response, consistent with the exclude={"medical_information"}/
    minimum-necessary pattern used elsewhere."""
    donors = db.query(DonorProfile).filter(DonorProfile.availability_status == "active").all()

    candidates = []
    for d in donors:
        candidates.append({
            "id": d.id,
            "blood_group": d.blood_group,
            "organs": d.organs_available or [],
        })

    def score_fn(c: dict) -> float:
        score = 0.0
        if c["blood_group"] == blood_group.upper():
            score += 50.0
        if any(organ.lower() in o.lower() for o in c["organs"]):
            score += 50.0
        return score

    classical_res = classical_search(candidates, score_fn)
    quantum_res = quantum_inspired_search(candidates, score_fn)

    return {
        "candidates_evaluated_count": len(candidates),
        "classical": {
            "evaluations": classical_res["evaluations"],
            "best_score": classical_res["best_score"],
            "best_donor_id": classical_res["best"]["id"] if classical_res["best"] else None
        },
        "quantum_inspired": {
            # Classical amplitude-amplification-style heuristic -- no
            # quantum hardware involved and no guaranteed speedup. This
            # ratio reflects evaluation count on this run only, not a
            # theoretical or proven advantage.
            "evaluations": quantum_res["evaluations"],
            "best_score": quantum_res["best_score"],
            "best_donor_id": quantum_res["best"]["id"] if quantum_res["best"] else None,
            "evaluation_ratio_this_run": f"{classical_res['evaluations'] / max(1, quantum_res['evaluations']):.2f}x",
            "same_optimum_found": classical_res["best"]["id"] == quantum_res["best"]["id"] if classical_res["best"] and quantum_res["best"] else None
        }
    }
