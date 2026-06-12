from __future__ import annotations

import logging

try:
    import langdetect
except ImportError:
    langdetect = None

logger = logging.getLogger(__name__)

# Map of ISO 639-1 language codes to language names
LANGUAGES = {
    "en": {"name": "English", "nativeName": "English"},
    "es": {"name": "Spanish", "nativeName": "Español"},
    "fr": {"name": "French", "nativeName": "Français"},
    "de": {"name": "German", "nativeName": "Deutsch"},
    "zh": {"name": "Chinese", "nativeName": "中文"},
    "ja": {"name": "Japanese", "nativeName": "日本語"},
    "ko": {"name": "Korean", "nativeName": "한국어"},
    "ru": {"name": "Russian", "nativeName": "Русский"},
    "it": {"name": "Italian", "nativeName": "Italiano"},
    "pt": {"name": "Portuguese", "nativeName": "Português"},
    "hi": {"name": "Hindi", "nativeName": "हिन्दी"},
    "ar": {"name": "Arabic", "nativeName": "العربية"},
    "nl": {"name": "Dutch", "nativeName": "Nederlands"},
    "pl": {"name": "Polish", "nativeName": "Polski"},
    "tr": {"name": "Turkish", "nativeName": "Türkçe"},
    "vi": {"name": "Vietnamese", "nativeName": "Tiếng Việt"},
    # Add more as needed for the 100+ languages
}


def get_language_name(code: str) -> str:
    """Return the English name of the language for a given ISO 639-1 code."""
    data = LANGUAGES.get(code.lower())
    return data["name"] if data else "Unknown Language"


def detect_language(text: str) -> str:
    """
    Detect the ISO 639-1 language code of the given text using langdetect.
    Returns 'en' as fallback if detection fails or is unavailable.
    """
    if not langdetect:
        logger.warning("langdetect not installed. Falling back to 'en'.")
        return "en"

    if not text.strip():
        return "en"

    try:
        detected = langdetect.detect(text)
        # Handle cases where langdetect returns locale-specific codes (e.g., zh-cn)
        return detected.split("-")[0]
    except Exception as e:
        logger.error("Language detection failed: %s", e)
        return "en"
