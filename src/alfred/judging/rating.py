"""The Robot Rating Ladder — Alfred's rating system, themed on famous fictional bots.

A 0..100 comedy score becomes a rating out of 5, rounded to the nearest quarter,
and the band it lands in is named after a beloved fictional robot / AI — so you
get verdicts like:

    95  ->  4¾/5  —  Johnny Five ⚡   "Number Five is ALIVE — and killing it!"
    70  ->  3½/5   —  Chappie 🎨       "Chappie made a funny, no?"
     0  ->  0/5    —  HAL 9000 🔴      "I'm sorry, Dave. That wasn't funny."

The ladder runs from a humourless menace at the bottom to a born entertainer at
the top. The full universe of robot names we can theme around lives in
docs/ROBOT_NAMES.md; the ones chosen for the ladder are below.
"""

from __future__ import annotations

from dataclasses import dataclass

MAX_RATING = 5.0

# Quarter-fraction glyphs for the pretty printer.
_FRACTIONS = {0.0: "", 0.25: "¼", 0.5: "½", 0.75: "¾"}

# The ladder: (minimum rating inclusive, robot name, emoji, quip). Highest first.
# Anchored so 3½ == Chappie and 4¾ == Johnny Five, per the channel's house style.
ROBOT_LADDER: list[tuple[float, str, str, str]] = [
    (5.00, "Bender",                    "🍺", "I'm 40% punchline, baby!"),
    (4.75, "Johnny Five",               "⚡", "Number Five is ALIVE — and killing it!"),
    (4.50, "Data",                      "🖖", "I have just engaged my humor subroutine."),
    (4.00, "Optimus Prime",             "🚛", "Comedy is the right of all sentient beings."),
    (3.50, "Chappie",                   "🎨", "Chappie made a funny, no?"),
    (3.00, "R2-D2",                     "🔵", "beep-boop (translation: that one landed)."),
    (2.50, "WALL·E",                    "🌱", "Waaall-eee… aww, so close."),
    (1.75, "C-3PO",                     "🟡", "The odds of that being funny were 3,720 to 1."),
    (1.00, "Robby the Robot",           "🤖", "Earnest. Mechanical. Not quite there."),
    (0.25, "Marvin the Paranoid Android", "🫠", "Brain the size of a planet, used for THAT."),
    (0.00, "HAL 9000",                  "🔴", "I'm sorry, Dave. I'm afraid that wasn't funny."),
]


def _band(value: float) -> tuple[str, str, str]:
    for threshold, name, emoji, quip in ROBOT_LADDER:
        if value >= threshold:
            return name, emoji, quip
    last = ROBOT_LADDER[-1]
    return last[1], last[2], last[3]


@dataclass(frozen=True)
class Rating:
    score: float       # original 0..100
    value: float       # 0..5 in 0.25 steps
    robot: str         # the fictional robot/AI this band is named after
    emoji: str
    quip: str

    def number(self) -> str:
        """The rating as a fractioned numeral, e.g. '4¾' or '½' or '3'."""
        whole = int(self.value)
        frac_glyph = _FRACTIONS.get(round(self.value - whole, 2), "")
        if whole == 0 and frac_glyph:
            return frac_glyph             # "½"
        return f"{whole}{frac_glyph}"     # "4¾"

    def pretty(self) -> str:
        """e.g. '4¾/5 — Johnny Five ⚡'."""
        return f"{self.number()}/5 — {self.robot} {self.emoji}"

    def stars(self) -> str:
        """A quick visual bar out of 5 (full / half blocks)."""
        full = int(self.value)
        half = (self.value - full) >= 0.5
        return "🤖" * full + ("🔩" if half else "") + "·" * (5 - full - (1 if half else 0))


def score_to_rating(score: float) -> Rating:
    """Map a 0..100 comedy score onto the Robot Rating Ladder (nearest quarter)."""
    score = max(0.0, min(100.0, score))
    raw = score / 100.0 * MAX_RATING
    value = round(raw * 4) / 4  # snap to nearest 0.25
    value = max(0.0, min(MAX_RATING, value))
    robot, emoji, quip = _band(value)
    return Rating(score=score, value=value, robot=robot, emoji=emoji, quip=quip)
