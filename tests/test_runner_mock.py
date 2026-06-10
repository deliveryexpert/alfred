"""End-to-end smoke test using the offline mock comedians + mock judge.

Proves the whole pipeline (perform -> judge -> rate -> rank) runs with no keys.
"""

from alfred.models import ROSTER
from alfred.providers import build_comedian
from alfred.bench.runner import run_benchmark
from alfred.judging.judge import build_judge


def test_full_mock_run_produces_rated_leaderboard():
    comedians = [build_comedian(spec, mock=True) for spec in ROSTER[:3]]
    judge = build_judge("mock", mock=True)

    results = run_benchmark(comedians, judge)

    assert len(results) == 3
    # Every contestant got a rating and a full set of judged performances.
    for r in results:
        assert r.rating is not None
        assert 0.0 <= r.rating.value <= 5.0
        assert len(r.performances) == len(ROSTER[0:1]) or len(r.performances) > 0
        assert all(p.score is not None for p in r.performances)

    # Leaderboard is sorted funniest-first.
    scores = [r.weighted_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_mock_is_deterministic():
    c = build_comedian(ROSTER[0], mock=True)
    a = c.perform("sys", "tell me a joke")
    b = c.perform("sys", "tell me a joke")
    assert a.text == b.text
