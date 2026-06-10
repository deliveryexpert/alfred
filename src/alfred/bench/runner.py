"""Stage the comedy benchmark: collect each contestant's bits, then judge them."""

from __future__ import annotations

from dataclasses import dataclass, field

from alfred.bench.prompts import CHALLENGES, COMEDIAN_SYSTEM, Challenge
from alfred.providers.base import Comedian, ProviderError
from alfred.judging.rating import Rating, score_to_rating


@dataclass
class Performance:
    """One contestant's response to one challenge, plus its judged score."""

    challenge: Challenge
    text: str
    score: float | None = None       # 0..100 from the judge, None if not yet judged
    judge_notes: str = ""
    error: str | None = None         # set if the model failed to respond


@dataclass
class BenchmarkResult:
    """A single contestant's full set, aggregate score, and Guffaw rating."""

    contestant: str
    performances: list[Performance] = field(default_factory=list)
    rating: Rating | None = None     # filled in once judged

    @property
    def weighted_score(self) -> float:
        """Weighted mean of the per-challenge scores (0..100)."""
        num = 0.0
        den = 0.0
        for p in self.performances:
            if p.score is None:
                continue
            num += p.score * p.challenge.weight
            den += p.challenge.weight
        return num / den if den else 0.0


def perform_all(comedian: Comedian, challenges: list[Challenge] | None = None) -> BenchmarkResult:
    """Ask one contestant every challenge (no judging yet)."""
    challenges = challenges or CHALLENGES
    result = BenchmarkResult(contestant=comedian.name)
    for ch in challenges:
        try:
            reply = comedian.perform(COMEDIAN_SYSTEM, ch.prompt, max_tokens=400)
            result.performances.append(Performance(challenge=ch, text=reply.text))
        except ProviderError as e:
            result.performances.append(
                Performance(challenge=ch, text="", error=str(e))
            )
    return result


def run_benchmark(comedians: list[Comedian], judge) -> list[BenchmarkResult]:
    """Run the full show: every contestant performs, the judge scores, ratings assigned.

    `judge` is any object with `.score(challenge, contestant, text) -> (float, str)`
    returning a 0..100 score and a short note. See alfred.judging.judge.
    """
    results = [perform_all(c) for c in comedians]

    for result in results:
        for p in result.performances:
            if p.error:
                p.score = 0.0
                p.judge_notes = "did not perform"
                continue
            score, notes = judge.score(p.challenge, result.contestant, p.text)
            p.score = score
            p.judge_notes = notes
        result.rating = score_to_rating(result.weighted_score)

    # Funniest first.
    results.sort(key=lambda r: r.weighted_score, reverse=True)
    return results
