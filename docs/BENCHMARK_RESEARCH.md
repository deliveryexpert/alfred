# 🔬 How Real AI Benchmarks Work — and What Alfred Borrows

Research notes on how established LLM benchmarks analyse model capabilities and
how their authors designed and implemented them — then how those lessons map
onto Alfred's comedy benchmark. (Requested research; sources at the bottom.)

---

## The four families of LLM evaluation

| Family | What it measures | Examples | How it's scored |
|---|---|---|---|
| **Static knowledge / reasoning** | Did the model get the *right answer*? | MMLU, GPQA, MATH | Auto-graded vs. a gold key (multiple-choice / exact match). |
| **Agentic / task completion** | Can it *do the job* end-to-end? | SWE-bench, WebArena | Did the test suite pass? Pass@k. |
| **Human preference (in the wild)** | Which answer do *people* prefer? | Chatbot Arena (LMSYS) | Blind pairwise votes → Elo / Bradley-Terry. |
| **LLM-as-judge** | Approximate human preference, cheaply | MT-Bench, AlpacaEval | A strong model scores/compares outputs against a rubric. |

Alfred is fundamentally a **subjective-quality** benchmark, so it lives in the
bottom two rows — the same place "which model writes better?" lives. That's the
hard part of eval, and it's exactly where the design choices below matter.

---

## How each landmark benchmark was built

### MMLU — *broad multiple-choice knowledge* (2020)
- **Design:** ~16,000 multiple-choice questions across 57 subjects, sourced from
  real exams/textbooks. Auto-graded against the correct letter.
- **Lesson:** breadth + objective grading made it cheap to run and hard to game…
  until models **saturated** it (>88%), and it could no longer separate the top.
- **For Alfred:** a single number saturates. Use *multiple categories* (we do —
  10 comedy "muscles") and be ready to **rotate the test** as models improve.

### GPQA — *PhD-level, "Google-proof"* (2023)
- **Design:** 448 expert-written science questions, validated by other experts,
  and **verified hard** by checking that skilled non-experts *with web access*
  still fail (~34% vs. ~65% for PhDs). The "Diamond" subset is the clean core.
- **Implementation pattern:** *expert-write → expert-validate → non-expert-test.*
- **For Alfred:** the comedy analogue is *write jokes-prompts → have comedians/
  judges validate → confirm they actually discriminate* (a prompt every model
  aces tells you nothing — drop it).

### SWE-bench — *real-world task completion* (2023)
- **Design:** drop the model into a real GitHub repo and ask it to fix a real
  bug; grade by **running the project's own test suite**. No rubric needed —
  the world grades you.
- **Caution:** scores jumped ~2% → ~72% in a year, and a human-filtered pass
  removed ~⅓ of tasks as ambiguous/infeasible. **Ambiguous tasks poison a
  benchmark.**
- **For Alfred:** keep prompts unambiguous; if judges wildly disagree on a bit,
  the *prompt* may be the problem, not the model.

### HELM — *holistic, multi-metric* (Stanford, 2022)
- **Design:** evaluate every model across **7 dimensions per scenario**
  (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency)
  over 42 scenarios — explicitly surfacing *where* models fail, not just a
  single leaderboard number.
- **For Alfred:** mirrored directly in our **5-dimension rubric** (wit,
  originality, timing, on-brief, landing). A model can be witty but rambling;
  the breakdown shows it.

### Chatbot Arena (LMSYS) — *human preference at scale* (2023)
- **Design:** users see **two anonymous models** answer the same prompt, vote
  for the better one. Blind + pairwise removes brand bias and the impossibility
  of scoring an answer in a vacuum.
- **Math:** votes feed an **Elo** rating (later **Bradley-Terry**, which assumes
  skill is fixed and computes a maximum-likelihood rating from all pairwise
  results — more stable, with confidence intervals).
- **For Alfred:** this is the gold standard for subjective quality, and the
  model behind our proposed **pairwise-ELO tournament** judging mode.

### MT-Bench — *LLM-as-judge, formalised* (2023)
- **Design:** 80 curated multi-turn questions across 8 categories; a strong
  model (GPT-4) scores answers 1–10 against a rubric, or judges pairwise.
- **Key finding:** GPT-4's verdicts **agree with humans ~80%** of the time —
  about the same as humans agree with each other — *which makes LLM-as-judge a
  legitimate, scalable proxy.*
- **Known biases to control:** position bias (order of the two answers),
  verbosity bias (longer looks better), and self-enhancement bias (a judge
  favours its own outputs).
- **For Alfred:** this is the backbone of our default **panel judge**. We adopt
  its bias mitigations: randomise/anonymise, and a judge never scores a
  contestant from its own lab.

---

## The cross-cutting lessons (what the survivors share)

Benchmarks that survived scrutiny (HELM, GPQA Diamond, SWE-bench, Chatbot Arena)
tend to share these properties — and Alfred is built to honour them:

1. **Construct clarity.** Be explicit about what you claim to measure. → our
   rubric *is* the operational definition of "funny."
2. **The rubric matters more than the judge's reasoning.** LLM-judge reliability
   hinges on a clear rubric, not on chain-of-thought. → keep rubric dimensions
   concrete and few.
3. **Blind + pairwise beats absolute scoring** for subjective quality. → offered
   as the pairwise-ELO mode (`JUDGING_BRAINSTORM.md`).
4. **Control known biases** (position, verbosity, self-preference). → anonymise,
   randomise order, exclude same-lab judging.
5. **Multi-dimensional > single number.** → 10 categories × 5 rubric dims.
6. **Plan for saturation & contamination.** A fixed public test gets gamed and
   maxed out. → rotate a fresh hidden prompt set per episode.
7. **Validate the items, not just the models.** A prompt every model aces, or
   that judges can't agree on, is a *broken item* — cut it.
8. **Calibrate the judge against humans.** Periodically have a human rate a
   sample and check the panel agrees (MT-Bench's ~80% bar).

---

## Where Alfred sits

Alfred is a *deliberately playful* subjective benchmark, but it's engineered
with the same bones as the serious ones: identical conditions, a multi-dimension
rubric (HELM-style), an LLM-judge proxy calibrated to humans (MT-Bench-style),
an optional blind pairwise tournament (Arena-style), and item-validation +
rotation to fight saturation. The only un-serious part is the unit on the
scoreboard — a Johnny Five instead of an Elo point.

---

## Sources

- [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena (Zheng et al.) — arXiv](https://arxiv.org/html/2306.05685v4)
- [Chatbot Arena: Benchmarking LLMs in the Wild with Elo Ratings — LMSYS](https://www.lmsys.org/blog/2023-05-03-arena/)
- [Chatbot Arena: New models & Elo system update (Bradley-Terry) — LMSYS](https://www.lmsys.org/blog/2023-12-07-leaderboard/)
- [LLM-as-a-judge: a complete guide — Evidently AI](https://www.evidentlyai.com/llm-guide/llm-as-a-judge)
- [Custom AI Benchmark Guide: lessons from public evals — Kili](https://kili-technology.com/blog/custom-ai-benchmark-guide-what-the-best-public-evals-teach-you-about-building-your-own)
- [AI Benchmarks Explained: GPQA, SWE-bench & Arena Elo — Nanonets](https://nanonets.com/blog/ai-benchmarks-explained-gpqa-swe-bench-chatbot-arena/)
- [Language model benchmark — Wikipedia](https://en.wikipedia.org/wiki/Language_model_benchmark)
