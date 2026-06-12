from __future__ import annotations

import logging

from app.core.config import settings
from app.services.ai.base_provider import BaseTranslationProvider
from app.services.ai.openai_provider import OpenAIProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.groq_provider import GroqProvider

logger = logging.getLogger(__name__)

# Registry: model_id → (ProviderClass, model_name, required_key_attr)
_PROVIDER_REGISTRY: dict[str, tuple[type[BaseTranslationProvider], str, str]] = {
    "gpt-4o":                  (OpenAIProvider, "gpt-4o",                    "OPENAI_API_KEY"),
    "gpt-4o-mini":             (OpenAIProvider, "gpt-4o-mini",               "OPENAI_API_KEY"),
    "gemini-1.5-pro":          (GeminiProvider, "gemini-1.5-pro",            "GOOGLE_API_KEY"),
    "gemini-2.0-flash":        (GeminiProvider, "gemini-2.0-flash",          "GOOGLE_API_KEY"),
    "llama-3.1-70b":           (GroqProvider,   "llama-3.1-70b-versatile",   "GROQ_API_KEY"),
    "llama-3.1-8b":            (GroqProvider,   "llama-3.1-8b-instant",      "GROQ_API_KEY"),
    "mixtral-8x7b":            (GroqProvider,   "mixtral-8x7b-32768",        "GROQ_API_KEY"),
}

# Fallback order: try these in order if the requested model's key is missing
_FALLBACK_ORDER = ["gemini-1.5-pro", "llama-3.1-70b", "gpt-4o-mini", "gpt-4o"]


def _has_key(key_attr: str) -> bool:
    """Check if an API key is configured (not empty / placeholder)."""
    val = getattr(settings, key_attr, "")
    return bool(val) and not val.startswith("your-") and not val.startswith("sk-your")


class ProviderFactory:
    """
    Strategy Pattern Factory.
    Resolves the correct AI provider at runtime based on model identifier.
    Auto-falls-back to an available provider if the requested model's API key is missing.
    """

    @staticmethod
    def get_provider(model: str) -> BaseTranslationProvider:
        entry = _PROVIDER_REGISTRY.get(model)
        if entry is None:
            raise ValueError(
                f"Unknown model '{model}'. "
                f"Available: {list(_PROVIDER_REGISTRY.keys())}"
            )

        provider_class, model_name, key_attr = entry

        # If the key is configured, use this provider directly
        if _has_key(key_attr):
            logger.info("Using provider: %s (model: %s)", provider_class.__name__, model_name)
            return provider_class(model=model_name)

        # Key missing — auto-fallback to first available provider
        logger.warning(
            "API key for model '%s' (%s) not configured. Attempting fallback...",
            model, key_attr
        )
        for fallback_model in _FALLBACK_ORDER:
            if fallback_model == model:
                continue
            fallback_entry = _PROVIDER_REGISTRY.get(fallback_model)
            if fallback_entry and _has_key(fallback_entry[2]):
                fb_class, fb_model_name, _ = fallback_entry
                logger.warning(
                    "Falling back to: %s (model: %s)", fb_class.__name__, fb_model_name
                )
                return fb_class(model=fb_model_name)

        raise ValueError(
            "No AI provider is configured. Please add at least one API key to your .env file:\n"
            "  - OPENAI_API_KEY  (https://platform.openai.com/api-keys)\n"
            "  - GOOGLE_API_KEY  (https://aistudio.google.com/app/apikey — FREE)\n"
            "  - GROQ_API_KEY    (https://console.groq.com/keys — FREE)"
        )

    @staticmethod
    def available_models() -> list[dict]:
        """Return only models whose API keys are configured."""
        all_models = [
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "provider": "Google",
                "description": "Google's most capable model — FREE tier",
                "key_attr": "GOOGLE_API_KEY",
            },
            {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "provider": "Google",
                "description": "Google's fastest model — FREE tier",
                "key_attr": "GOOGLE_API_KEY",
            },
            {
                "id": "llama-3.1-70b",
                "name": "Llama 3.1 70B (Groq)",
                "provider": "Groq",
                "description": "Meta's Llama via Groq — FREE tier, very fast",
                "key_attr": "GROQ_API_KEY",
            },
            {
                "id": "llama-3.1-8b",
                "name": "Llama 3.1 8B Instant (Groq)",
                "provider": "Groq",
                "description": "Fastest model via Groq — FREE tier",
                "key_attr": "GROQ_API_KEY",
            },
            {
                "id": "mixtral-8x7b",
                "name": "Mixtral 8x7B (Groq)",
                "provider": "Groq",
                "description": "Great for long documents — FREE tier",
                "key_attr": "GROQ_API_KEY",
            },
            {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "provider": "OpenAI",
                "description": "Most capable GPT model, best quality",
                "key_attr": "OPENAI_API_KEY",
            },
            {
                "id": "gpt-4o-mini",
                "name": "GPT-4o Mini",
                "provider": "OpenAI",
                "description": "Fast and cost-effective GPT model",
                "key_attr": "OPENAI_API_KEY",
            },
        ]
        # Return all models, mark which ones are available based on configured keys
        result = []
        for m in all_models:
            key_attr = m.pop("key_attr")
            m["available"] = _has_key(key_attr)
            result.append(m)
        return result
