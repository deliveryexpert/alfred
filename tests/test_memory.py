"""Memory protocol: a run can be saved, reloaded, and aggregated into standings."""

from alfred import memory
from alfred.models import ROSTER
from alfred.providers import build_comedian
from alfred.bench.runner import run_benchmark
from alfred.judging.judge import build_judge


def _mock_run():
    comedians = [build_comedian(spec, mock=True) for spec in ROSTER[:3]]
    return run_benchmark(comedians, build_judge("mock", mock=True))


def test_save_and_load_roundtrip(tmp_path):
    results = _mock_run()
    record = memory.to_record(results, mock=True, judge="mock", judge_model="n/a")
    path = memory.save_run(record, directory=tmp_path)

    assert path.exists()
    loaded = memory.load_run(path)
    assert loaded["run_id"] == record["run_id"]
    assert len(loaded["results"]) == 3
    # rank, score, rating and per-challenge bits survive the round trip
    top = loaded["results"][0]
    assert top["rank"] == 1
    assert top["rating"]["robot"]
    assert top["performances"][0]["text"]


def test_history_and_standings(tmp_path):
    # Save two runs into the same store.
    for _ in range(2):
        rec = memory.to_record(_mock_run(), mock=True, judge="mock", judge_model="n/a")
        # force distinct run ids so both files persist
        rec["run_id"] = rec["run_id"] + "-" + str(id(rec))[-4:]
        memory.save_run(rec, directory=tmp_path)

    history = memory.load_history(tmp_path)
    assert len(history) == 2

    table = memory.standings(history)
    assert table  # non-empty
    # Each contestant appeared in both runs; winner has at least one win.
    assert all(rec.appearances == 2 for rec in table)
    assert sum(rec.wins for rec in table) == 2  # one winner per run
    # Standings sorted by average score, best first.
    scores = [rec.avg_score for rec in table]
    assert scores == sorted(scores, reverse=True)


def test_canonical_name_merges_mock_variants():
    assert memory._canonical("Claude Opus 4.8 (mock)") == "Claude Opus 4.8"


def test_standings_markdown_empty():
    md = memory.standings_markdown([])
    assert "All-Time Comedy Standings" in md
    assert "No contests on record" in md


def test_write_standings_from_history(tmp_path):
    rec = memory.to_record(_mock_run(), mock=True, judge="mock", judge_model="n/a")
    memory.save_run(rec, directory=tmp_path)

    out = tmp_path / "STANDINGS.md"
    memory.write_standings(out, directory=tmp_path)

    text = out.read_text(encoding="utf-8")
    assert "Episodes on record: **1**" in text
    assert "| # | Contestant |" in text
    assert "Chappie" in text or "R2-D2" in text  # a robot rating rendered
