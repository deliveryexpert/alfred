# 🧑‍⚖️ Judging — Brainstorm & Decisions

You asked to **brainstorm the judging engine further** before locking it in. This
is that brainstorm. The codebase is built so the judge is *pluggable* — every
judge implements one method, `score(challenge, contestant, text) -> (0..100,
note)` — so we can try any of these without touching the runner.

Grounding: the options below are shaped by how real subjective-quality
benchmarks judge models (Chatbot Arena, MT-Bench, HELM). See
`BENCHMARK_RESEARCH.md`.

---

## The options on the table

### 1. Rubric panel (AI judges scoring 0–10 per dimension) — **built, current default**
A judge model scores each bit against the 5-dimension rubric; scores are weighted
into 0–100. With several judges, we average (a *panel*).
- ➕ Simple, explainable, cheap, gives a per-dimension breakdown.
- ➕ MT-Bench shows single-answer LLM grading correlates ~80% with humans.
- ➖ Absolute scores drift (one judge's "7" ≠ another's); susceptible to
  verbosity/self-preference bias.
- **Mitigations in code:** explicit rubric; a judge never scores its own lab's
  contestant (`_same_lab`).

### 2. Blind pairwise tournament → ELO / Bradley-Terry — **recommended next step**
Don't score in a vacuum — show the judge **two anonymised bits** for the same
challenge and ask "which is funnier?" Aggregate wins into an ELO (or
Bradley-Terry) rating, exactly like Chatbot Arena.
- ➕ Humans (and LLMs) are far better at *comparing* than at *absolute scoring*.
- ➕ Naturally removes "what does 73/100 even mean" drift; yields confidence
  intervals.
- ➖ More API calls (O(n²) pairs, or smart Swiss-style pairing); needs an ELO
  layer. We'd convert final ELO → the 0–5 Robot ladder for display.

### 3. Human-rated CLI — **built (`--judge human`)**
Print each bit blind, you score 0–10 in the terminal.
- ➕ Real laughs, ground truth.
- ➖ Slow, doesn't scale; great as a *calibration* sample to check the panel
  agrees with you (the MT-Bench ~80%-agreement check).

### 4. Hybrid (AI draft + human override)
Panel produces a draft score; a human can bump any bit. Best of both, more UI.

### 5. Audience / social signal (channel-native, longer-term)
Since this feeds a social channel: post the (blinded) bits, let **real engagement**
(votes, likes) feed back as a score. The most authentic "did people laugh?"
signal — but slow and gameable; best as a *seasonal* overlay, not the per-run
judge.

---

## Biases we must control (from the LLM-judge literature)

- **Position bias** — judge favours the first/second option → randomise order in
  pairwise mode.
- **Verbosity bias** — longer looks "better" → our *timing* rubric dimension
  penalises padding; cap `max_tokens`.
- **Self-enhancement bias** — a judge over-rates its own family → already
  excluded via `_same_lab`.
- **Self-consistency** — re-ask or use a panel and average to reduce variance.

---

## Recommendation

1. **Keep the rubric panel as the default** (built, explainable, good for the
   per-dimension graphics).
2. **Add a blind pairwise-ELO mode** as the headline "championship" ranking —
   it's the Arena-grade method and the most defensible "who's funniest."
3. **Use human judging as periodic calibration** (sample ~10% of bits, confirm
   the panel agrees ≥~80%).
4. Defer audience-signal until the channel has reach.

Open questions for you:
- For the panel, **one judge or several**? (A 3-model panel — e.g. Claude +
  Gemini + GPT, each excluded from its own lab — is more robust but 3× the
  cost.)
- Should the **headline ranking** be rubric-panel or pairwise-ELO?
- Do you want **human calibration** wired into each episode, or only when a
  result looks off?

Tell me and I'll wire the chosen path in (the pairwise-ELO module is the main
piece of new code).
