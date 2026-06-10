"""OpenAI-compatible adapter.

Covers OpenAI itself plus every vendor that exposes the OpenAI Chat Completions
API shape: xAI (Grok), Mistral, Groq (Llama), Together, DeepSeek, etc. — just
point `base_url` at the right host (see alfred/models.py).
"""

from __future__ import annotations

from alfred.providers.base import ProviderError, Reply


class OpenAICompatibleComedian:
    def __init__(
        self,
        name: str,
        model_id: str,
        api_key: str,
        base_url: str | None = None,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as e:  # pragma: no cover - import guard
            raise ProviderError(
                "The 'openai' package is required for OpenAI-compatible models "
                "(GPT, Grok, Mistral, Llama, DeepSeek...). "
                'Install it with: pip install "openai>=1.40"'
            ) from e

        self.name = name
        self.model_id = model_id
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def perform(self, system: str, user: str, *, max_tokens: int = 1024) -> Reply:
        try:
            resp = self._client.chat.completions.create(
                model=self.model_id,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        except Exception as e:  # noqa: BLE001
            raise ProviderError(f"{self.name}: {e}") from e

        text = (resp.choices[0].message.content or "").strip()
        return Reply(text=text, model_name=self.name, raw=resp)
