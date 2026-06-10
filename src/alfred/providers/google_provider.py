"""Google (Gemini) adapter — uses the official `google-genai` SDK."""

from __future__ import annotations

from alfred.providers.base import ProviderError, Reply


class GoogleComedian:
    def __init__(self, name: str, model_id: str, api_key: str) -> None:
        try:
            from google import genai
        except ImportError as e:  # pragma: no cover - import guard
            raise ProviderError(
                "The 'google-genai' package is required for Gemini models. "
                'Install it with: pip install "google-genai>=0.3"'
            ) from e

        self.name = name
        self.model_id = model_id
        self._genai = genai
        self._client = genai.Client(api_key=api_key)

    def perform(self, system: str, user: str, *, max_tokens: int = 1024) -> Reply:
        try:
            resp = self._client.models.generate_content(
                model=self.model_id,
                contents=user,
                config=self._genai.types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=max_tokens,
                ),
            )
        except Exception as e:  # noqa: BLE001
            raise ProviderError(f"{self.name}: {e}") from e

        return Reply(text=(resp.text or "").strip(), model_name=self.name, raw=resp)
