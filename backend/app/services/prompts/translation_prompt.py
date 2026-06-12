def build_translation_prompt(
    source_text: str,
    source_language: str,
    target_language: str,
    tone: str = "formal",
) -> str:
    """
    Build the user-facing translation prompt.

    Args:
        source_text: The text to be translated.
        source_language: ISO 639-1 source language code, or 'auto'.
        target_language: ISO 639-1 target language code.
        tone: Translation tone (casual/formal/technical/literary).

    Returns:
        Formatted prompt string ready to send as a user message.
    """
    src = "the detected language" if source_language == "auto" else source_language

    return (
        f"Translate the following text from {src} to {target_language}.\n"
        f"Tone: {tone}\n\n"
        f"Text to translate:\n"
        f"---\n"
        f"{source_text}\n"
        f"---"
    )


def build_batch_translation_prompt(
    items: list[dict],
) -> str:
    """
    Build a batch translation prompt for multiple text items.

    Args:
        items: List of dicts with keys: text, source_language, target_language, tone

    Returns:
        Combined prompt string for batch translation.
    """
    lines = ["Translate each of the following items. Return a JSON array of results.\n"]
    for i, item in enumerate(items, 1):
        lines.append(
            f"Item {i}: [{item['source_language']} → {item['target_language']}] "
            f"(tone: {item['tone']})\n{item['text']}\n"
        )
    return "\n".join(lines)
