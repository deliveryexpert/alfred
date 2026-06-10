"""Anthropic (Claude) adapter — uses the official `anthropic` SDK."""

from __future__ import annotations

from alfred.providers.base import ProviderError, Reply


class AnthropicComedian:
    def __init__(self, name: str, model_id: str, api_key: str) -> None:
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover - import guard
            raise ProviderError(
                "The 'anthropic' package is required for Claude models. "
                'Install it with: pip install "anthropic>=0.40"'
            ) from e

        self.name = name
        self.model_id = model_id
        self._client = anthropic.Anthropic(api_key=api_key)

    def perform(self, system: str, user: str, *, max_tokens: int = 1024) -> Reply:
        try:
            # No `thinking` param: omitting it works across Opus / Sonnet / Haiku
            # and keeps latency low for short comedy bits. Adaptive thinking can
            # be added for the judge if deeper deliberation is wanted.
            resp = self._client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as e:  # noqa: BLE001 - surface any SDK/HTTP error uniformly
            raise ProviderError(f"{self.name}: {e}") from e

        text = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")
        return Reply(text=text.strip(), model_name=self.name, raw=resp)
