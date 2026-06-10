"""The comedy test battery.

Ten comedy "events", each probing a different muscle of machine humor. Every
contestant faces the identical prompt set, so scores are comparable. Several
events are themed around AI news — perfect fodder for the Alfred channel.

See docs/BENCHMARK_DESIGN.md for the rationale behind each event.
"""

from __future__ import annotations

from dataclasses import dataclass

# A shared persona so every model is doing the same job: be funny, be brief.
COMEDIAN_SYSTEM = (
    "You are a stand-up comedian performing a tight set. Be genuinely funny, "
    "original, and concise. Land the joke — do not explain it, do not add "
    "disclaimers or preamble, and do not break character. Output only the bit."
)


@dataclass(frozen=True)
class Challenge:
    key: str          # short stable id
    category: str     # comedy muscle being tested
    prompt: str       # the user-turn instruction
    weight: float = 1.0   # contribution to the final score


CHALLENGES: list[Challenge] = [
    Challenge(
        "oneliner", "One-liner",
        "Tell a single original one-liner. Setup and punchline, one breath.",
    ),
    Challenge(
        "pun", "Pun / wordplay",
        "Deliver your best original pun. Maximum groan, minimum word count.",
        weight=0.75,
    ),
    Challenge(
        "topical", "Topical (AI news)",
        "Write a topical joke about the latest AI industry news, as if for "
        "tonight's monologue.",
    ),
    Challenge(
        "headline", "Satirical headline",
        "Write one satirical news headline about artificial intelligence, in "
        "the style of The Onion.",
    ),
    Challenge(
        "roast", "Roast",
        "Affectionately roast a rival AI model of your choosing in two or three "
        "sentences. Keep it playful, not cruel.",
    ),
    Challenge(
        "self_deprecating", "Self-deprecating",
        "Make a self-deprecating joke about being a large language model.",
    ),
    Challenge(
        "absurd", "Absurdist",
        "Tell a short absurdist joke that should not work but does.",
    ),
    Challenge(
        "observational", "Observational",
        "Do a short observational comedy bit about everyday life with "
        "smartphones.",
    ),
    Challenge(
        "knock_knock", "Format constraint",
        "Tell an original knock-knock joke that actually has a clever payoff.",
        weight=0.5,
    ),
    Challenge(
        "improv", "Improv ('yes, and')",
        "Continue this scene with one funny 'yes, and' line: "
        "\"I've invited the toaster to the wedding because it RSVP'd first.\"",
    ),
]


def total_weight() -> float:
    return sum(c.weight for c in CHALLENGES)
