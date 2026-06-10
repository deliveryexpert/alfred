"""The common interface every model adapter implements."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ProviderError(RuntimeError):
    """Raised when a provider can't be reached or returns an error."""


@dataclass
class Reply:
    """A single model response to a single prompt."""

    text: str
    model_name: str
    raw: object | None = None  # The underlying SDK response, for debugging.


class Comedian(Protocol):
    """Anything that can take the stage: produces text from a system+user prompt."""

    name: str

    def perform(self, system: str, user: str, *, max_tokens: int = 1024) -> Reply:
        """Generate a response. Raises ProviderError on failure."""
        ...
