"""Memory protocol — persist benchmark runs so Alfred remembers past episodes.

Every run is saved as a JSON record under `runs/`, which is committed to git so
the scoreboard is permanent and survives across sessions. From that history we
can rebuild all-time standings, track each contestant's record, and later seed a
persistent ELO/championship rating.

A run record is plain JSON (no pickling), so it's safe to read, diff, and ship.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from alfred.bench.runner import BenchmarkResult
from alfred.judging.rating import Rating, score_to_rating

DEFAULT_DIR = Path("runs")
SCHEMA_VERSION = 1


def run_id_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


# --------------------------------------------------------------------------- #
# Serialisation                                                               #
# --------------------------------------------------------------------------- #

def _rating_to_dict(r: Rating | None) -> dict | None:
    if r is None:
        return None
    return {"score": r.score, "value": r.value, "robot": r.robot, "emoji": r.emoji}


def to_record(
    results: list[BenchmarkResult],
    *,
    mock: bool,
    judge: str,
    judge_model: str,
    run_id: str | None = None,
) -> dict:
    """Turn an in-memory run into a JSON-serialisable record."""
    run_id = run_id or run_id_now()
    return {
        "schema": SCHEMA_VERSION,
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mock": mock,
        "judge": judge,
        "judge_model": judge_model,
        "results": [
            {
                "contestant": r.contestant,
                "rank": rank,
                "score": round(r.weighted_score, 2),
                "rating": _rating_to_dict(r.rating),
                "performances": [
                    {
                        "challenge": p.challenge.key,
                        "category": p.challenge.category,
                        "score": p.score,
                        "text": p.text,
                        "judge_notes": p.judge_notes,
                        "error": p.error,
                    }
                    for p in r.performances
                ],
            }
            for rank, r in enumerate(results, 1)
        ],
    }


# --------------------------------------------------------------------------- #
# Store                                                                       #
# --------------------------------------------------------------------------- #

def save_run(record: dict, directory: Path = DEFAULT_DIR) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"run-{record['run_id']}.json"
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def list_run_files(directory: Path = DEFAULT_DIR) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("run-*.json"))


def load_run(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_history(directory: Path = DEFAULT_DIR) -> list[dict]:
    """All past runs, oldest first."""
    return [load_run(p) for p in list_run_files(directory)]


# --------------------------------------------------------------------------- #
# Aggregation                                                                 #
# --------------------------------------------------------------------------- #

@dataclass
class ContestantRecord:
    contestant: str
    appearances: int = 0
    wins: int = 0               # times finished #1
    total_score: float = 0.0
    best_score: float = 0.0

    @property
    def avg_score(self) -> float:
        return self.total_score / self.appearances if self.appearances else 0.0

    @property
    def rating(self) -> Rating:
        return score_to_rating(self.avg_score)


def standings(history: list[dict]) -> list[ContestantRecord]:
    """All-time standings across every saved run, best average first."""
    table: dict[str, ContestantRecord] = {}
    for run in history:
        for entry in run.get("results", []):
            name = _canonical(entry["contestant"])
            rec = table.setdefault(name, ContestantRecord(contestant=name))
            score = float(entry.get("score") or 0.0)
            rec.appearances += 1
            rec.total_score += score
            rec.best_score = max(rec.best_score, score)
            if entry.get("rank") == 1:
                rec.wins += 1
    return sorted(table.values(), key=lambda r: r.avg_score, reverse=True)


def _canonical(name: str) -> str:
    """Collapse '(mock)' variants so a contestant has one record across runs."""
    return name.replace(" (mock)", "").strip()
