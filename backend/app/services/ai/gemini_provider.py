from __future__ import annotations

import json
import logging

import google.generativeai as genai

from app.core.config import settings
from app.services.ai.base_provider import (
    BaseTranslationProvider,
    TranslationRequest,
    TranslationResult,
)
from app.services.prompts.system_prompts import TRANSLATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiProvider(BaseTranslationProvider):
    """
    AI translation provider backed by Google Gemini models.
    Supports: gemini-1.5-pro
    """

    def __init__(self, model: str = "gemini-1.5-pro") -> None:
        self.model = model
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self._genai_model = genai.GenerativeModel(
            model_name=model,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )

    def get_model_name(self) -> str:
        return self.model

    async def translate(self, request: TranslationRequest) -> TranslationResult:
        system_prompt = TRANSLATION_SYSTEM_PROMPT.format(tone=request.tone)
        user_prompt = self._build_structured_prompt(request)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Run synchronously inside an executor to avoid blocking asyncio
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._genai_model.generate_content(full_prompt),
        )

        raw_content = response.text or "{}"

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            data = {"translated_text": raw_content}

        return TranslationResult(
            translated_text=data.get("translated_text", ""),
            confidence_score=float(data.get("confidence_score", 0.88)),
            alternative_translations=data.get("alternative_translations", []),
            translator_notes=data.get("notes"),
            tokens_used=None,
            model_used=self.model,
        )
