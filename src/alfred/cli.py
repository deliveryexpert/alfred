"""`alfred` command-line entry point.

Examples
--------
    alfred list                 # who's ready to perform (which keys you have)
    alfred run --mock           # full dry run, no keys, no network
    alfred run                   # real run: every contestant with a key, AI panel
    alfred run --judge human     # you rate the bits yourself, blind
"""

from __future__ import annotations

import argparse
import sys

from alfred.config import RunConfig
from alfred.models import ROSTER, ModelSpec, by_name
from alfred.providers import build_comedian, available
from alfred.providers.base import ProviderError
from alfred.bench.runner import run_benchmark, BenchmarkResult
from alfred.judging.judge import build_judge
from alfred import memory


def _build_contestants(mock: bool):
    comedians = []
    for spec, reason in available(ROSTER, mock=mock):
        if reason:
            continue
        try:
            comedians.append(build_comedian(spec, mock=mock))
        except ProviderError as e:
            print(f"  ! skipping {spec.name}: {e}", file=sys.stderr)
    return comedians


def _build_panel(judge_model: str, mock: bool):
    if mock:
        return build_judge("mock", mock=True)
    spec = by_name_for_model(judge_model)
    try:
        judge_comedian = build_comedian(spec, mock=False)
    except ProviderError as e:
        print(f"Cannot build judge ({e}). Falling back to --mock judge.", file=sys.stderr)
        return build_judge("mock", mock=True)
    return build_judge("panel", mock=False, judges=[judge_comedian])


def by_name_for_model(model_id: str) -> ModelSpec:
    """Find a roster spec by model id, else assume an Anthropic judge."""
    for spec in ROSTER:
        if spec.model_id == model_id:
            return spec
    return ModelSpec(f"Judge {model_id}", "anthropic", model_id, ("ANTHROPIC_API_KEY",))


def cmd_list(args: argparse.Namespace) -> int:
    print("Alfred comedy roster:\n")
    for spec, reason in available(ROSTER, mock=args.mock):
        status = "✅ ready" if not reason else f"⏭️  {reason}"
        print(f"  {spec.emoji} {spec.name:<22} {spec.model_id:<22} {status}")
    print("\nFill in keys in .env (copy .env.example) to enable more contestants.")
    return 0


def _print_leaderboard(results: list[BenchmarkResult]) -> None:
    print("\n" + "=" * 60)
    print("🏆  ALFRED COMEDY LEADERBOARD")
    print("=" * 60)
    for rank, r in enumerate(results, 1):
        rating = r.rating
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f" {rank}.")
        line = f"{medal} {r.contestant:<24} "
        line += rating.pretty() if rating else "unrated"
        print(line)
        if rating:
            print(f"      {rating.stars()}   ({r.weighted_score:.1f}/100)")
    print("=" * 60)


def _print_details(results: list[BenchmarkResult]) -> None:
    for r in results:
        print(f"\n--- {r.contestant} — {r.rating.pretty() if r.rating else ''} ---")
        for p in r.performances:
            score = f"{p.score:.0f}" if p.score is not None else "—"
            print(f"  [{p.challenge.category}] {score}/100")
            body = p.error or p.text
            print(f"    {body}")
            if p.judge_notes:
                print(f"    ↳ {p.judge_notes}")


def cmd_run(args: argparse.Namespace) -> int:
    RunConfig(mock=args.mock, judge_model=args.judge_model)  # validate knobs

    comedians = _build_contestants(args.mock)
    if not comedians:
        print(
            "No contestants available. Add API keys to .env, or try: alfred run --mock",
            file=sys.stderr,
        )
        return 1

    judge = build_judge(args.judge, mock=args.mock, judges=None) if args.judge != "panel" \
        else _build_panel(args.judge_model, args.mock)

    print(f"🎤 Staging the comedy benchmark with {len(comedians)} contestant(s)...")
    results = run_benchmark(comedians, judge)

    _print_leaderboard(results)
    if args.details:
        _print_details(results)

    if not args.no_save:
        record = memory.to_record(
            results, mock=args.mock, judge=args.judge, judge_model=args.judge_model
        )
        path = memory.save_run(record)
        print(f"\n🧠 Run remembered: {path}  (alfred history)")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    history = memory.load_history()
    if not history:
        print("No runs remembered yet. Run one: alfred run --mock")
        return 0

    print(f"📚 {len(history)} run(s) on record\n")
    for run in reversed(history):  # newest first
        results = run.get("results", [])
        winner = results[0]["contestant"] if results else "—"
        tag = " (mock)" if run.get("mock") else ""
        print(f"  {run['run_id']}{tag}  {len(results)} contestants  🥇 {winner}")

    print("\n" + "=" * 60)
    print("🏛️  ALL-TIME STANDINGS  (average across every run)")
    print("=" * 60)
    for rank, rec in enumerate(memory.standings(history), 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f" {rank}.")
        rating = rec.rating
        print(f"{medal} {rec.contestant:<24} {rating.pretty()}")
        print(f"      {rec.appearances} run(s) · {rec.wins} win(s) · "
              f"avg {rec.avg_score:.1f} · best {rec.best_score:.1f}/100")
    print("=" * 60)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="alfred",
        description="Rate AI models on comedy, in Guffaws.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="show the roster and which contestants are ready")
    p_list.add_argument("--mock", action="store_true", help="treat everyone as ready")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="run the comedy benchmark")
    p_run.add_argument("--mock", action="store_true",
                       help="offline dry run — no API keys or network needed")
    p_run.add_argument("--judge", choices=["panel", "human", "mock"], default="panel",
                       help="how to score the bits (default: AI panel)")
    p_run.add_argument("--judge-model", default="claude-opus-4-8",
                       help="model id for the AI panel judge")
    p_run.add_argument("--details", action="store_true",
                       help="print every bit and per-challenge score")
    p_run.add_argument("--no-save", action="store_true",
                       help="don't write this run to memory (runs/)")
    p_run.set_defaults(func=cmd_run)

    p_hist = sub.add_parser("history", help="show past runs and all-time standings")
    p_hist.set_defaults(func=cmd_history)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
