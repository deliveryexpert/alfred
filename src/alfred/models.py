"""The roster of AI models Alfred can put on stage.

Each entry maps a friendly contestant name to a provider adapter + model id.

NOTE ON MODEL IDS: Anthropic's ids are verified current. The others are
sensible defaults — provider line-ups change often, so treat the non-Anthropic
ids as editable and confirm against each provider's docs before a "real" run.
You can always override the id per contestant here without touching any other
code.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    name: str            # Contestant display name, e.g. "Claude Opus 4.8".
    provider: str        # Adapter key: anthropic | openai_compatible | google | mock.
    model_id: str        # The provider's model identifier.
    key_env: tuple[str, ...] = ()   # Env var(s) that hold this provider's API key.
    base_url: str | None = None     # For OpenAI-compatible third parties.
    emoji: str = "🤖"


# The full line-up. Comment out any contestant you don't want on stage.
ROSTER: list[ModelSpec] = [
    # --- Anthropic (Claude) — ids verified current --------------------------
    ModelSpec("Claude Opus 4.8", "anthropic", "claude-opus-4-8", ("ANTHROPIC_API_KEY",), emoji="🎭"),
    ModelSpec("Claude Sonnet 4.6", "anthropic", "claude-sonnet-4-6", ("ANTHROPIC_API_KEY",), emoji="🎭"),
    ModelSpec("Claude Haiku 4.5", "anthropic", "claude-haiku-4-5", ("ANTHROPIC_API_KEY",), emoji="🎭"),

    # --- OpenAI (GPT) -------------------------------------------------------
    ModelSpec("GPT-5.1", "openai_compatible", "gpt-5.1", ("OPENAI_API_KEY",), emoji="🟢"),
    ModelSpec("GPT-4o", "openai_compatible", "gpt-4o", ("OPENAI_API_KEY",), emoji="🟢"),

    # --- Google (Gemini) ----------------------------------------------------
    ModelSpec("Gemini 2.5 Pro", "google", "gemini-2.5-pro", ("GOOGLE_API_KEY",), emoji="🔷"),
    ModelSpec("Gemini 2.5 Flash", "google", "gemini-2.5-flash", ("GOOGLE_API_KEY",), emoji="🔷"),

    # --- xAI (Grok) — OpenAI-compatible API ---------------------------------
    ModelSpec("Grok 4", "openai_compatible", "grok-4", ("XAI_API_KEY",),
              base_url="https://api.x.ai/v1", emoji="✖️"),

    # --- Mistral — OpenAI-compatible API ------------------------------------
    ModelSpec("Mistral Large", "openai_compatible", "mistral-large-latest", ("MISTRAL_API_KEY",),
              base_url="https://api.mistral.ai/v1", emoji="🌬️"),

    # --- Meta Llama (via Groq's OpenAI-compatible host) ---------------------
    ModelSpec("Llama 4 Maverick", "openai_compatible", "llama-4-maverick", ("GROQ_API_KEY",),
              base_url="https://api.groq.com/openai/v1", emoji="🦙"),

    # --- DeepSeek — OpenAI-compatible API -----------------------------------
    ModelSpec("DeepSeek V3", "openai_compatible", "deepseek-chat", ("DEEPSEEK_API_KEY",),
              base_url="https://api.deepseek.com", emoji="🐋"),
]


def by_name(name: str) -> ModelSpec | None:
    for spec in ROSTER:
        if spec.name.lower() == name.lower():
            return spec
    return None
