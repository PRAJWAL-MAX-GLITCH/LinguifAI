from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from app.schemas.common import AppBaseModel


# ── Enums as string literals ───────────────────────────────────────────────────

TONE_OPTIONS = ("casual", "formal", "technical", "literary")
MODEL_OPTIONS = ("gpt-4o", "gpt-4o-mini", "gemini-1.5-pro", "gemini-1.5-flash", "deepseek-chat")


# ── Request Schemas ────────────────────────────────────────────────────────────

class TranslationRequest(AppBaseModel):
    source_text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="The text to translate",
    )
    source_language: str = Field(
        default="auto",
        min_length=2,
        max_length=10,
        description="ISO 639-1 source language code, or 'auto' for detection",
    )
    target_language: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="ISO 639-1 target language code",
    )
    tone: str = Field(
        default="formal",
        description=f"Translation tone. One of: {TONE_OPTIONS}",
    )
    model: str = Field(
        default="gpt-4o",
        description=f"AI model to use. One of: {MODEL_OPTIONS}",
    )
    include_alternatives: bool = Field(
        default=True,
        description="Include alternative translation suggestions",
    )

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str) -> str:
        if v not in TONE_OPTIONS:
            raise ValueError(f"tone must be one of: {TONE_OPTIONS}")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        if v not in MODEL_OPTIONS:
            raise ValueError(f"model must be one of: {MODEL_OPTIONS}")
        return v


class BatchTranslationRequest(AppBaseModel):
    items: List[TranslationRequest] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of translation requests (max 10)",
    )


class DetectLanguageRequest(AppBaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


# ── Response Schemas ───────────────────────────────────────────────────────────

class TranslationResponse(AppBaseModel):
    id: uuid.UUID
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: Optional[float] = None
    alternative_translations: Optional[List[str]] = None
    translator_notes: Optional[str] = None
    latency_ms: Optional[int] = None
    model_used: str
    tone: str
    is_starred: bool = False
    created_at: datetime


class DetectLanguageResponse(AppBaseModel):
    detected_language: str
    language_name: str
    confidence: float


class TranslationListResponse(AppBaseModel):
    id: uuid.UUID
    source_language: str
    target_language: str
    source_text: str
    translated_text: str
    ai_model: str
    tone: str
    confidence_score: Optional[float] = None
    is_starred: bool
    char_count: Optional[int] = None
    created_at: datetime
