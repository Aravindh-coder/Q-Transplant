"""
Benchmark harness: compares classical_search vs quantum_inspired_search on
the same candidate pool and score function, across pool sizes. Reports
evaluations used, whether the same optimum was found, and wall-clock time.
Print or log the raw output — do not summarize it as a blanket "faster."
"""
import time
from typing import Callable

from app.services.quantum.search import classical_search, quantum_inspired_search


def run_benchmark(candidates: list[dict], score_fn: Callable[[dict], float], seed: int | None = 42) -> dict:
    t0 = time.perf_counter()
    classical = classical_search(candidates, score_fn)
    t1 = time.perf_counter()
    quantum_inspired = quantum_inspired_search(candidates, score_fn, seed=seed)
    t2 = time.perf_counter()

    same_optimum = (
        classical["best"] is not None and quantum_inspired["best"] is not None and
        classical["best_score"] == quantum_inspired["best_score"]
    )

    return {
        "pool_size": len(candidates),
        "classical": {**classical, "time_seconds": round(t1 - t0, 6)},
        "quantum_inspired": {**quantum_inspired, "time_seconds": round(t2 - t1, 6)},
        "same_optimum_found": same_optimum,
        "evaluation_reduction_pct": (
            round((1 - quantum_inspired["evaluations"] / classical["evaluations"]) * 100, 1)
            if classical["evaluations"] else None
        ),
    }


def run_benchmark_suite(candidate_factory: Callable[[int], list[dict]], score_fn: Callable[[dict], float],
                         pool_sizes: list[int] = (50, 200, 1000, 5000)) -> list[dict]:
    """Runs run_benchmark across several pool sizes to see how the trade-off scales."""
    return [run_benchmark(candidate_factory(n), score_fn) for n in pool_sizes]
