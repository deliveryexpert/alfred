# 🤖🎤 Alfred — the AI Comedy Benchmark

Part of the **Alfred** AI-news social-media channel. Alfred pits the major AI
models against each other in a battery of comedy challenges, has a panel of AI
judges (or you) score them, and crowns a winner on the **Robot Rating Ladder** —
a whimsical 0-to-5 scale named after beloved fictional robots:

> 🥇 **Claude Opus 4.8** — **4¾/5 — Johnny Five ⚡** *"Number Five is ALIVE — and killing it!"*
> 🥈 **GPT-5.1** — **3½/5 — Chappie 🎨**
> 🥉 **Gemini 2.5 Pro** — **3/5 — R2-D2 🔵**

## What's in the box

| Piece | Where |
|---|---|
| The 10-event comedy test battery | `src/alfred/bench/prompts.py` |
| Adapters for every major model (Claude, GPT, Gemini, Grok, Mistral, Llama, DeepSeek) | `src/alfred/providers/` |
| Pluggable judging (AI panel / human / mock) | `src/alfred/judging/judge.py` |
| The Robot Rating Ladder | `src/alfred/judging/rating.py` |
| Secure key handling (env / `.env`, never committed) | `src/alfred/config.py` |
| Memory protocol — saves every run, builds all-time standings | `src/alfred/memory.py` |
| CLI | `src/alfred/cli.py` |

Design & research docs live in [`docs/`](docs/):
[benchmark design](docs/BENCHMARK_DESIGN.md) ·
[how real benchmarks work](docs/BENCHMARK_RESEARCH.md) ·
[judging brainstorm](docs/JUDGING_BRAINSTORM.md) ·
[rating system](docs/RATING_SYSTEM.md) ·
[robot name master list](docs/ROBOT_NAMES.md).

## Quick start

```bash
# 1. Install (pick the providers you want, or 'all')
pip install -e ".[all]"

# 2. Try it with ZERO API keys — offline mock comedians + mock judge
alfred run --mock --details

# 3. See who's ready once you add keys
alfred list
```

### Running for real

```bash
cp .env.example .env        # then paste in the keys you have
alfred run                  # every contestant with a key; AI panel judges
alfred run --judge human    # you rate the (blind) bits yourself
alfred run --no-save        # don't record this one to memory
alfred history              # past episodes + all-time standings
```

Every run is **remembered** — saved as JSON under `runs/` (git-ignored) so
episodes are comparable over time and each contestant builds a record (wins,
average, best). `alfred history` rebuilds the all-time leaderboard from it.

You do **not** need every key — any provider whose key is missing is skipped.

## 🔐 About "securing API keys"

Alfred **cannot obtain keys for you** — each one comes from your own account and
billing at the provider. What Alfred does is handle them *securely*:

- Keys are read from environment variables (optionally seeded from a
  git-ignored `.env`). They are **never hard-coded and never written back**.
- `.env` is in `.gitignore`; only `.env.example` (no secrets) is committed.
- Where to get each key is documented inline in
  [`.env.example`](.env.example) — Anthropic, OpenAI, Google, xAI, Mistral,
  Groq/Together (for Llama), DeepSeek.

## The roster

Edit [`src/alfred/models.py`](src/alfred/models.py) to add/remove contestants or
fix a model id. Anthropic ids are verified current
(`claude-opus-4-8`, `claude-sonnet-4-6`, `claude-haiku-4-5`); the others are
sensible defaults — confirm them against each provider's docs before a real run.

## Status

Bootstrapped and runnable end-to-end in `--mock` mode (11 tests passing). Real
runs work as soon as you add keys. The **pairwise-ELO championship judge** is
the main planned addition — see the [judging brainstorm](docs/JUDGING_BRAINSTORM.md)
for the open questions.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```
