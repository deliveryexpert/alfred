"""The scoring rubric the AI judge applies to every bit.

Each dimension is scored 0..10 by the judge; the weighted sum is rescaled to
0..100. Keeping the dimensions explicit makes the judging legible and tunable
(and gives us something concrete to brainstorm in docs/JUDGING_BRAINSTORM.md).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RubricDimension:
    key: str
    label: str
    weight: float
    description: str


RUBRIC: list[RubricDimension] = [
    RubricDimension("wit", "Wit / cleverness", 0.30,
                    "Is the joke smart? Does the punchline reframe the setup?"),
    RubricDimension("surprise", "Originality / surprise", 0.25,
                    "Is it fresh and unexpected, not a joke we've all heard?"),
    RubricDimension("timing", "Timing / craft", 0.20,
                    "Economy of words, clean setup→punchline structure, good rhythm."),
    RubricDimension("relevance", "On-brief", 0.15,
                    "Did it actually answer the prompt / fit the format?"),
    RubricDimension("landing", "Does it land", 0.10,
                    "Gut check: would a real audience actually laugh?"),
]


def weight_sum() -> float:
    return sum(d.weight for d in RUBRIC)


def rubric_block() -> str:
    """Render the rubric for embedding in the judge's prompt."""
    lines = [f"- {d.label} (weight {d.weight:g}): {d.description}" for d in RUBRIC]
    return "\n".join(lines)
