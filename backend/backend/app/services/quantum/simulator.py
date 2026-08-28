"""Classical simulator helpers for quantum-inspired search experiments."""
import math

def grover_iteration_count(n: int) -> int:
    if n <= 0: return 0
    return max(1, round(math.pi/4 * math.sqrt(n)))

def amplitude_distribution(n: int, marked: int, iterations: int | None = None) -> list[float]:
    """Toy Grover amplitude model for visualization/research, not hardware."""
    if n <= 0 or not 0 <= marked < n: return []
    k=iterations if iterations is not None else grover_iteration_count(n)
    theta=math.asin(1/math.sqrt(n))
    marked_amp=math.sin((2*k+1)*theta)
    other_amp=math.cos((2*k+1)*theta)/math.sqrt(max(1,n-1)) if n>1 else 0
    return [marked_amp if i==marked else other_amp for i in range(n)]
