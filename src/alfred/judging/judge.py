"""Judges that turn a comedy bit into a 0..100 score.

Three implementations, all sharing one interface — `score(challenge, contestant,
text) -> (score, note)`:

* PanelJudge  — one or more AI models score each bit against the rubric. Bits are
                anonymised and a judge never scores its own contestant name,
                which dampens self-preference bias. Panel scores are averaged.
* HumanJudge  — prints each bit blind and asks you to rate it in the terminal.
* MockJudge   — deterministic offline scoring, for --mock runs and tests.

The judging approach is deliberately pluggable — we're still brainstorming the
"right" engine (pairwise ELO tournament, audience signal, etc.). See
docs/JUDGING_BRAINSTORM.md.
"""

from __future__ import annotations

import hashlib
import json
import re

from alfred.bench.prompts import Challenge
from alfred.judging.rubric import RUBRIC, rubric_block, weight_sum
from alfred.providers.base import Comedian, ProviderError

_JUDGE_SYSTEM = (
    "You are a seasoned comedy critic on a judging panel. You are fair, hard to "
    "impress, and immune to flattery. Score strictly on how funny the material "
    "is. Always respond with ONLY a JSON object, no prose."
)


def _judge_prompt(challenge: Challenge, text: str) -> str:
    keys = ", ".join(f'"{d.key}"' for d in RUBRIC)
    return (
        f"A comedian was given this challenge ({challenge.category}):\n"
        f"  {challenge.prompt}\n\n"
        f"They responded with:\n"
        f'  """{text}"""\n\n'
        f"Score the bit on each rubric dimension from 0 (unfunny) to 10 "
        f"(hilarious):\n{rubric_block()}\n\n"
        f"Respond with ONLY this JSON shape:\n"
        f'{{"scores": {{{keys}}}, "note": "<=12 word verdict"}}'
    )


def _parse_scores(raw_text: str) -> tuple[dict[str, float], str]:
    """Pull the {scores, note} JSON out of a model reply, leniently."""
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("no JSON found in judge reply")
    data = json.loads(match.group(0))
    scores = {d.key: float(data.get("scores", {}).get(d.key, 0)) for d in RUBRIC}
    note = str(data.get("note", "")).strip()
    return scores, note


def _weighted_0_100(scores: dict[str, float]) -> float:
    total = sum(min(10.0, max(0.0, scores.get(d.key, 0.0))) * d.weight for d in RUBRIC)
    return total / (10.0 * weight_sum()) * 100.0


class PanelJudge:
    """Average the verdicts of one or more AI judges."""

    def __init__(self, judges: list[Comedian]) -> None:
        if not judges:
            raise ValueError("PanelJudge needs at least one judge model")
        self.judges = judges

    def score(self, challenge: Challenge, contestant: str, text: str) -> tuple[float, str]:
        if not text.strip():
            return 0.0, "no material"

        prompt = _judge_prompt(challenge, text)
        panel_scores: list[float] = []
        notes: list[str] = []
        for judge in self.judges:
            # Skip a judge scoring its own contestant (anti-self-preference).
            if _same_lab(judge.name, contestant):
                continue
            try:
                reply = judge.perform(_JUDGE_SYSTEM, prompt, max_tokens=200)
                scores, note = _parse_scores(reply.text)
            except (ProviderError, ValueError):
                continue
            panel_scores.append(_weighted_0_100(scores))
            if note:
                notes.append(f"{judge.name}: {note}")

        if not panel_scores:
            return 0.0, "panel could not score"
        avg = sum(panel_scores) / len(panel_scores)
        return avg, " | ".join(notes)


class MockJudge:
    """Deterministic offline scoring for --mock and tests."""

    def score(self, challenge: Challenge, contestant: str, text: str) -> tuple[float, str]:
        if not text.strip():
            return 0.0, "no material"
        h = int(hashlib.sha256((contestant + challenge.key + text).encode()).hexdigest(), 16)
        score = 35.0 + (h % 600) / 10.0  # spread across ~35..95
        return score, "mock verdict"


class HumanJudge:
    """Ask the human at the keyboard to rate each (anonymised) bit."""

    def score(self, challenge: Challenge, contestant: str, text: str) -> tuple[float, str]:
        if not text.strip():
            return 0.0, "no material"
        print(f"\n[{challenge.category}] (contestant hidden)")
        print(f'  "{text}"')
        while True:
            raw = input("  Your score 0-10 (Enter=5): ").strip()
            if raw == "":
                return 50.0, "human: 5"
            try:
                val = max(0.0, min(10.0, float(raw)))
                return val * 10.0, f"human: {val:g}"
            except ValueError:
                print("  Please enter a number 0-10.")


def _same_lab(judge_name: str, contestant: str) -> bool:
    """Crude family check so e.g. a Claude judge won't score a Claude contestant."""
    families = ["claude", "gpt", "gemini", "grok", "mistral", "llama", "deepseek"]
    jn, cn = judge_name.lower(), contestant.lower()
    return any(f in jn and f in cn for f in families)


def build_judge(kind: str, *, mock: bool, judges: list[Comedian] | None = None):
    """Factory: 'panel' | 'human' | 'mock'."""
    if mock or kind == "mock":
        return MockJudge()
    if kind == "human":
        return HumanJudge()
    if kind == "panel":
        return PanelJudge(judges or [])
    raise ValueError(f"unknown judge kind: {kind}")
