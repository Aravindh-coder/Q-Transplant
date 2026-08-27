from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DonorProfile
from app.services.quantum.search import classical_search, quantum_inspired_search
from app.services.quantum.benchmark import run_benchmark
from app.services.quantum.grover_sim import simulate_grover_steps

router = APIRouter(prefix="/api/v1/quantum", tags=["quantum"])

@router.get("/grover-sim")
def get_grover_simulation(n_candidates: int = Query(64, ge=4, le=1000), target_index: int = Query(3, ge=0)):
    return {
        "n_candidates": n_candidates,
        "target_index": target_index,
        "theoretical_optimal_iterations": max(1, int(round((3.14159 / 4.0) * (n_candidates ** 0.5)))),
        "steps": simulate_grover_steps(n_candidates, target_index)
    }

@router.get("/benchmark")
def get_quantum_benchmark(n_values: str = "10,100,500,1000"):
    n_list = [int(x.strip()) for x in n_values.split(",") if x.strip().isdigit()]
    return run_benchmark(n_list)

@router.get("/search-donors")
def search_donors_quantum(organ: str, blood_group: str, db: Session = Depends(get_db)):
    donors = db.query(DonorProfile).filter(DonorProfile.availability_status == "active").all()
    
    candidates = []
    for d in donors:
        candidates.append({
            "id": d.id,
            "name": f"Donor {d.id[:8]}",
            "blood_group": d.blood_group,
            "organs": d.organs_available or [],
            "hla": {"hla_a": d.hla_a, "hla_b": d.hla_b, "hla_c": d.hla_c, "hla_dr": d.hla_dr, "hla_dq": d.hla_dq}
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
        "quantum_grover": {
            "evaluations": quantum_res["evaluations"],
            "best_score": quantum_res["best_score"],
            "best_donor_id": quantum_res["best"]["id"] if quantum_res["best"] else None,
            "speedup_ratio": f"{classical_res['evaluations'] / max(1, quantum_res['evaluations']):.2f}x"
        }
    }
