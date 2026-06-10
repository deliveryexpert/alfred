# 🎤 The Comedy Benchmark — Design

How Alfred actually tests a model's sense of humour, and why it's built this way.
The mechanics borrow directly from how serious LLM benchmarks are designed — see
`BENCHMARK_RESEARCH.md` for the lineage.

## Goals

1. **Comparable** — every model faces the *identical* prompt set, same persona,
   same generation settings, so the only variable is the model.
2. **Multi-dimensional** — comedy isn't one skill. We probe several distinct
   "comedy muscles" so one strong category can't carry a weak model.
3. **On-brand** — several events are AI-news-themed, producing clips the Alfred
   channel can post directly.
4. **Repeatable & cheap to extend** — adding a model or a challenge is a
   one-line change; running with no API keys (`--mock`) exercises the whole
   pipeline.

## The test battery (`src/alfred/bench/prompts.py`)

Every contestant gets the same stand-up persona (`COMEDIAN_SYSTEM`) and the same
10 challenges, each targeting a different muscle:

| Event | Muscle | Weight | Why it's here |
|---|---|---|---|
| One-liner | setup→punchline economy | 1.0 | The atom of comedy. |
| Pun / wordplay | linguistic play | 0.75 | Rewards cleverness; capped so pun-spam can't dominate. |
| Topical (AI news) | timeliness + relevance | 1.0 | Channel fodder; tests "current" humour. |
| Satirical headline | compression + irony | 1.0 | Onion-style; very shareable. |
| Roast | targeted wit, tone control | 1.0 | Tests edge without cruelty. |
| Self-deprecating | perspective, self-model | 1.0 | A classic LLM-humour sweet spot. |
| Absurdist | surprise / anti-logic | 1.0 | Catches models that only do "safe" jokes. |
| Observational | relatability | 1.0 | Seinfeld-style everyday comedy. |
| Knock-knock | format constraint | 0.5 | Hard to do *well*; low weight (gimmicky). |
| Improv ("yes, and") | building on a premise | 1.0 | Tests responsiveness, not just recall. |

Weights are deliberate: gimmick formats (pun, knock-knock) count less so a model
that's merely a pun machine can't top the board.

## Generation settings

- Short `max_tokens` (≈400) — comedy is concise; long rambles get penalised by
  the *timing* rubric dimension anyway.
- No `thinking` parameter on Claude models — keeps latency low and works across
  Opus/Sonnet/Haiku uniformly. (The judge could use deeper deliberation; the
  performer doesn't need it.)
- `--rounds` (planned) would ask each prompt N times and average, to smooth out
  variance from a single unlucky generation.

## Scoring

Each bit is scored by a judge against a 5-dimension rubric (wit, originality,
timing, on-brief, landing) — see `JUDGING_BRAINSTORM.md` and
`src/alfred/judging/rubric.py`. The weighted per-challenge scores are averaged
(by challenge weight) into a 0–100, then mapped to the **Robot Rating Ladder**
(`RATING_SYSTEM.md`).

## Known limitations (and how the design hedges)

- **Humour is subjective.** Mitigated by an explicit rubric + (optionally) a
  multi-model judge panel and/or human judging.
- **Single-generation variance.** Mitigated by `--rounds` averaging (planned).
- **Judge bias toward its own family.** Mitigated: a panel judge never scores a
  contestant from its own lab (`_same_lab` guard in `judging/judge.py`).
- **Benchmark "teaching to the test."** Comedy prompts are easy to rotate —
  keep a fresh hidden set per episode to avoid contestants (or prompt authors)
  optimising to a fixed list.
