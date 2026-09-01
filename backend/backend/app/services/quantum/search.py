"""
Research module: classical vs. quantum-inspired candidate search.

This does NOT run on real quantum hardware and makes no claim of quantum
speedup. It implements a Grover-inspired *amplitude-amplification-style*
heuristic on classical hardware (a common "quantum-inspired" technique) and
benchmarks it honestly against linear/classical search. Report whatever the
benchmark actually shows — do not round up.

Usage:
    from app.services.quantum.search import classical_search, quantum_inspired_search
    from app.services.quantum.benchmark import run_benchmark
"""
import math
import random
from typing import Callable


def classical_search(candidates: list[dict], score_fn: Callable[[dict], float]) -> dict:
    """Linear scan — evaluates every candidate once. This is the baseline."""
    evaluations = 0
    best, best_score = None, -math.inf
    for c in candidates:
        s = score_fn(c)
        evaluations += 1
        if s > best_score:
            best, best_score = c, s
    return {"best": best, "best_score": best_score, "evaluations": evaluations}


def quantum_inspired_search(candidates: list[dict], score_fn: Callable[[dict], float],
                             iterations: int | None = None, seed: int | None = None) -> dict:
    """
    Amplitude-amplification-inspired heuristic: maintains a probability
    weight per candidate, biases sampling toward higher-scoring candidates
    each round (mirroring how Grover's algorithm amplifies the amplitude of
    marked states), and evaluates a shrinking sampled subset per round
    instead of the full set every time.

    This is a classical approximation technique, not a quantum algorithm —
    it can find a strong candidate in fewer evaluations on large pools, at
    the cost of not being guaranteed to find the true global optimum the
    way an exhaustive scan is. The benchmark module measures that trade-off
    directly rather than asserting it.
    """
    rng = random.Random(seed)
    n = len(candidates)
    if n == 0:
        return {"best": None, "best_score": -math.inf, "evaluations": 0}

    iterations = iterations or max(3, round(math.sqrt(n)))  # ~sqrt(n) rounds, Grover-inspired
    weights = [1.0] * n
    evaluations = 0
    best, best_score = None, -math.inf
    sample_size = max(1, round(n / iterations))

    for _ in range(iterations):
        total = sum(weights)
        probs = [w / total for w in weights]
        sample_idx = rng.choices(range(n), weights=probs, k=min(sample_size, n))
        for i in set(sample_idx):
            s = score_fn(candidates[i])
            evaluations += 1
            if s > best_score:
                best, best_score = candidates[i], s
            # amplify weight of good candidates, damp the rest — the
            # "amplitude amplification" analogy
            weights[i] *= 1.0 + max(0.0, s - best_score + 1.0) / (best_score + 1e-6 if best_score > 0 else 1.0)

    return {"best": best, "best_score": best_score, "evaluations": evaluations}


def quantum_inspired_search_traced(candidates: list[dict], score_fn: Callable[[dict], float],
                                    id_fn: Callable[[dict], str], iterations: int | None = None,
                                    seed: int | None = None) -> dict:
    """Same algorithm as quantum_inspired_search, but records a step-by-step
    trace of each round (which candidates were sampled, the running best,
    the amplitude weight distribution) so a frontend can animate the actual
    search happening instead of only showing a final number. Used by the
    live search demo endpoint; the honest pipeline-comparison metadata on
    every real match still uses the untraced version above to avoid the
    extra memory/serialization cost on every request."""
    rng = random.Random(seed)
    n = len(candidates)
    if n == 0:
        return {"best": None, "best_score": -math.inf, "evaluations": 0, "trace": []}

    iterations = iterations or max(3, round(math.sqrt(n)))
    weights = [1.0] * n
    evaluations = 0
    best, best_score, best_id = None, -math.inf, None
    sample_size = max(1, round(n / iterations))
    trace = []

    for it in range(iterations):
        total = sum(weights)
        probs = [w / total for w in weights]
        sample_idx = rng.choices(range(n), weights=probs, k=min(sample_size, n))
        sampled_ids = []
        for i in set(sample_idx):
            s = score_fn(candidates[i])
            evaluations += 1
            sampled_ids.append(id_fn(candidates[i]))
            if s > best_score:
                best, best_score, best_id = candidates[i], s, id_fn(candidates[i])
            weights[i] *= 1.0 + max(0.0, s - best_score + 1.0) / (best_score + 1e-6 if best_score > 0 else 1.0)
        top_weighted = sorted(range(n), key=lambda i: weights[i], reverse=True)[:5]
        max_w = max(weights) or 1.0
        trace.append({
            "iteration": it + 1,
            "sampled_candidate_ids": sampled_ids,
            "evaluations_so_far": evaluations,
            "best_so_far_id": best_id,
            "best_so_far_score": None if best_score == -math.inf else round(best_score, 2),
            "top_amplitudes": [{"id": id_fn(candidates[i]), "weight": round(weights[i] / max_w, 3)} for i in top_weighted],
        })

    return {"best": best, "best_score": best_score, "evaluations": evaluations, "trace": trace, "iterations": iterations, "candidates_searched": n}
