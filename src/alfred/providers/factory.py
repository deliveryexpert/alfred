"""Turn a ModelSpec into a live Comedian, or explain why we can't."""

from __future__ import annotations

from alfred.config import get_key
from alfred.models import ModelSpec
from alfred.providers.base import Comedian, ProviderError
from alfred.providers.mock import MockComedian


def build_comedian(spec: ModelSpec, *, mock: bool = False) -> Comedian:
    """Instantiate the adapter for `spec`.

    If `mock` is set, returns an offline MockComedian wearing the contestant's
    name (no key needed). Otherwise raises ProviderError if the API key for this
    provider is missing.
    """
    if mock:
        return MockComedian(name=f"{spec.name} (mock)")

    api_key = get_key(*spec.key_env)
    if not api_key:
        raise ProviderError(
            f"No API key for {spec.name}: set {' or '.join(spec.key_env)} in your .env"
        )

    if spec.provider == "anthropic":
        from alfred.providers.anthropic_provider import AnthropicComedian

        return AnthropicComedian(spec.name, spec.model_id, api_key)

    if spec.provider == "openai_compatible":
        from alfred.providers.openai_compatible import OpenAICompatibleComedian

        return OpenAICompatibleComedian(spec.name, spec.model_id, api_key, spec.base_url)

    if spec.provider == "google":
        from alfred.providers.google_provider import GoogleComedian

        return GoogleComedian(spec.name, spec.model_id, api_key)

    raise ProviderError(f"Unknown provider '{spec.provider}' for {spec.name}")


def available(specs: list[ModelSpec], *, mock: bool = False) -> list[tuple[ModelSpec, str | None]]:
    """Report which contestants are ready to perform.

    Returns (spec, reason_unavailable). reason is None when the contestant is
    good to go. In mock mode everyone is available.
    """
    out: list[tuple[ModelSpec, str | None]] = []
    for spec in specs:
        if mock or get_key(*spec.key_env):
            out.append((spec, None))
        else:
            out.append((spec, f"missing {' or '.join(spec.key_env)}"))
    return out
