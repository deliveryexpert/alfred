"""Secure configuration: load API keys from the environment / a .gitignore'd .env.

Keys are NEVER hard-coded and NEVER written back to disk. We read them from
environment variables (optionally seeded from a local `.env` file) at runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    # Loads variables from a local `.env` if present. Does not override real
    # environment variables, and silently does nothing if the file is absent.
    load_dotenv()
except ImportError:  # python-dotenv is a hard dependency, but degrade gracefully.
    pass


def get_key(*env_vars: str) -> str | None:
    """Return the first non-empty value among the given environment variables."""
    for var in env_vars:
        value = os.environ.get(var)
        if value and value.strip():
            return value.strip()
    return None


@dataclass(frozen=True)
class RunConfig:
    """Top-level knobs for a benchmark run."""

    mock: bool = False           # Use the offline MOCK comedian/judge (no keys, no network).
    rounds: int = 1              # How many times to ask each prompt (averaged).
    judge_model: str = "claude-opus-4-8"  # Default judge (see judging/judge.py).
    seed: int | None = None      # Optional seed for reproducible prompt sampling.
