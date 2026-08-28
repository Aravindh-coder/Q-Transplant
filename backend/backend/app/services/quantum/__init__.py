"""Quantum-inspired research utilities. No real quantum speedup is claimed."""
from .search import classical_search, quantum_inspired_search
from .optimizer import optimize
from .benchmark import run_benchmark, run_benchmark_suite

__all__=["classical_search","quantum_inspired_search","optimize","run_benchmark","run_benchmark_suite"]
