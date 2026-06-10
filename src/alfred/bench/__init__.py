"""The comedy benchmark: the test prompts and the runner that stages them."""

from alfred.bench.prompts import CHALLENGES, Challenge
from alfred.bench.runner import run_benchmark, Performance, BenchmarkResult

__all__ = [
    "CHALLENGES",
    "Challenge",
    "run_benchmark",
    "Performance",
    "BenchmarkResult",
]
