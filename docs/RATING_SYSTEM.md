# 🤖 The Robot Rating Ladder

Alfred scores each contestant 0–100 internally (the weighted rubric average),
then converts that to a friendly **rating out of 5, rounded to the nearest
quarter** — and names the band after a beloved fictional robot or AI.

So instead of a boring "73.5/100", the channel says:

> **Claude Sonnet 4.6 earns a 3½ — Chappie 🎨** *("Chappie made a funny, no?")*

## The ladder (worst → funniest)

| Rating (of 5) | Robot | | Vibe |
|---|---|---|---|
| 0 | **HAL 9000** | 🔴 | "I'm sorry, Dave. I'm afraid that wasn't funny." |
| ¼ | **Marvin the Paranoid Android** | 🫠 | Brain the size of a planet, used for *that*. |
| 1 | **Robby the Robot** | 🤖 | Earnest, mechanical, not quite there. |
| 1¾ | **C-3PO** | 🟡 | "The odds of that being funny were 3,720 to 1." |
| 2½ | **WALL·E** | 🌱 | Waaall-eee… aww, so close. |
| 3 | **R2-D2** | 🔵 | beep-boop (translation: that one landed). |
| 3½ | **Chappie** | 🎨 | Chappie made a funny, no? |
| 4 | **Optimus Prime** | 🚛 | "Comedy is the right of all sentient beings." |
| 4½ | **Data** | 🖖 | "I have just engaged my humor subroutine." |
| 4¾ | **Johnny Five** | ⚡ | "Number Five is ALIVE — and killing it!" |
| 5 | **Bender** | 🍺 | "I'm 40% punchline, baby!" |

A score falls into a band by rounding to the nearest quarter, then taking the
highest robot whose threshold it meets. The ladder is anchored so that **3½ is
always a Chappie** and **4¾ is always a Johnny Five** — the two examples that
defined the house style.

## How the number is rendered

`Rating.number()` prints proper fraction glyphs: `4¾`, `3½`, `2¼`, or `½`.
`Rating.pretty()` gives the full lower-third: `4¾/5 — Johnny Five ⚡`.
`Rating.stars()` gives a quick bar: `🤖🤖🤖🔩·`.

## Swapping the theme

The whole ladder is one list — `ROBOT_LADDER` in
`src/alfred/judging/rating.py`. Want a different cast (all _Star Trek_, all
villains, all _Transformers_)? Reorder/rename that list; nothing else changes.
The full naming universe to pick from is `docs/ROBOT_NAMES.md`.

## Why 0–5 quarters (not 0–100)?

- **Legible on screen.** "4¾ Johnny Five" reads in half a second; "94.7%"
  doesn't, and invites false precision.
- **Comparable across episodes.** A fixed 0–5 scale lets viewers compare the
  March winner to the June winner at a glance.
- **The score is still there.** We keep the underlying 0–100 (`Rating.score`)
  for tie-breaks, trend charts, and analytics — it's just not the headline.
