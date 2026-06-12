from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TranslationRequest:
    """Unified translation request passed to all AI providers."""
    source_text: str
    source_language: str
    target_language: str
    tone: str = "formal"
    include_alternatives: bool = True


@dataclass
class TranslationResult:
    """Unified translation result returned by all AI providers."""
    translated_text: str
    confidence_score: float
    alternative_translations: List[str] = field(default_factory=list)
    translator_notes: Optional[str] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None


class BaseTranslationProvider(ABC):
    """
    Abstract Base Class for all AI translation providers.
    Enforces the Strategy Pattern architecture.
    """

    @abstractmethod
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        """Translate text and return a structured TranslationResult."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the canonical model identifier string."""
        pass

    def _build_structured_prompt(self, request: TranslationRequest) -> str:
        """
        Build the user-facing prompt string from a TranslationRequest.
        Shared across all providers.
        """
        return (
            f"Translate the following text from {request.source_language} "
            f"to {request.target_language}.\n"
            f"Tone: {request.tone}\n\n"
            f"Text to translate:\n{request.source_text}"
        )
