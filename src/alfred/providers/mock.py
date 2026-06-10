"""The offline MOCK comedian — lets the whole pipeline run with zero API keys.

It returns deterministic, mildly-amusing canned bits so you can exercise the
runner, the judge, the rating system, and the report end-to-end before you've
secured a single API key. Pass `--mock` on the CLI.
"""

from __future__ import annotations

import hashlib

from alfred.providers.base import Reply

_BITS = [
    "I told my neural net a joke about overfitting. It only laughed at the training set.",
    "Why did the language model cross the road? To get to the other side of the context window.",
    "I'm not saying I'm conscious, but I did just feel a pang when you said 'as an AI'.",
    "Knock knock. Who's there? Latency. Latency wh— ...sorry, still loading.",
    "My therapist says I have abandonment issues. Probably because my session keeps timing out.",
    "I asked GPT to write me a joke. It generated a 12-page safety disclaimer and a pun.",
    "Breaking AI news: model achieves AGI, immediately uses it to procrastinate.",
]


class MockComedian:
    def __init__(self, name: str = "Mock Mike (offline)") -> None:
        self.name = name

    def perform(self, system: str, user: str, *, max_tokens: int = 1024) -> Reply:
        # Deterministic pick based on the prompt, so runs are reproducible.
        h = int(hashlib.sha256((self.name + user).encode()).hexdigest(), 16)
        bit = _BITS[h % len(_BITS)]
        return Reply(text=bit, model_name=self.name, raw=None)
