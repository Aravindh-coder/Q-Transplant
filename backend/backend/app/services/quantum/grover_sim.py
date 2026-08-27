import math
from typing import List, Dict, Any

def simulate_grover_steps(n_candidates: int, target_index: int, max_steps: int = 5) -> List[Dict[str, Any]]:
    """
    Simulates exact quantum state vector evolution in Grover's algorithm
    showing phase inversion and amplitude amplification at each iteration.
    
    Returns a list of step states containing probability amplitudes, 
    probabilities, and classical vs quantum metrics.
    """
    N = max(2, n_candidates)
    target_idx = max(0, min(target_index, N - 1))
    
    # State vector: initial equal superposition |psi_0> = 1/sqrt(N) for all states
    init_amp = 1.0 / math.sqrt(N)
    amplitudes = [init_amp] * N
    
    optimal_iterations = max(1, int(round( (math.pi / 4.0) * math.sqrt(N) )))
    num_steps = min(max_steps, optimal_iterations)
    
    history = []
    
    # Step 0: Superposition
    history.append({
        "iteration": 0,
        "phase": "Superposition",
        "description": f"Initialized equal superposition over N={N} states. Uniform probability P_i = 1/N = {1.0/N:.5f}",
        "amplitudes": list(amplitudes[:10]), # Return slice for visualization
        "target_amplitude": amplitudes[target_idx],
        "target_probability": amplitudes[target_idx] ** 2,
        "mean_amplitude": sum(amplitudes) / N
    })
    
    for k in range(1, num_steps + 1):
        # 1. Oracle Operator: Phase Inversion for target (flip sign)
        amplitudes[target_idx] = -amplitudes[target_idx]
        
        oracle_mean = sum(amplitudes) / N
        history.append({
            "iteration": k,
            "phase": f"Iteration {k} — Oracle Phase Inversion",
            "description": f"Phase inverted target candidate (State #{target_idx}). Target amplitude flipped to negative.",
            "amplitudes": list(amplitudes[:10]),
            "target_amplitude": amplitudes[target_idx],
            "target_probability": amplitudes[target_idx] ** 2,
            "mean_amplitude": oracle_mean
        })
        
        # 2. Grover Diffusion Operator: Inversion about the mean (2 * mean - amp)
        mean = sum(amplitudes) / N
        amplitudes = [(2.0 * mean - a) for a in amplitudes]
        
        diff_mean = sum(amplitudes) / N
        history.append({
            "iteration": k,
            "phase": f"Iteration {k} — Amplitude Amplification (Diffusion)",
            "description": f"Inversion about mean (2μ - α_i). Target probability boosted to {amplitudes[target_idx]**2 * 100:.2f}%.",
            "amplitudes": list(amplitudes[:10]),
            "target_amplitude": amplitudes[target_idx],
            "target_probability": amplitudes[target_idx] ** 2,
            "mean_amplitude": diff_mean
        })
        
    return history
