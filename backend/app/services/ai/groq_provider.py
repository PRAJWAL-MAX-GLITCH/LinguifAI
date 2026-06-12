from __future__ import annotations

import json
import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.ai.base_provider import (
    BaseTranslationProvider,
    TranslationRequest,
    TranslationResult,
)
from app.services.prompts.system_prompts import TRANSLATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Groq uses OpenAI-compatible API — completely FREE tier available
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqProvider(BaseTranslationProvider):
    """
    AI translation provider backed by Groq (FREE alternative to DeepSeek).

    Groq offers free API access to:
    - llama-3.1-70b-versatile  (best quality, recommended)
    - llama-3.1-8b-instant     (fastest)
    - mixtral-8x7b-32768       (good for long texts)

    Get your FREE API key at: https://console.groq.com/keys
    Uses the OpenAI-compatible API interface.
    """

    def __init__(self, model: str = "llama-3.1-70b-versatile") -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
        )

    def get_model_name(self) -> str:
        return self.model

    async def translate(self, request: TranslationRequest) -> TranslationResult:
        system_prompt = TRANSLATION_SYSTEM_PROMPT.format(tone=request.tone)
        user_prompt = self._build_structured_prompt(request)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=4096,
        )

        raw_content = response.choices[0].message.content or "{}"
        tokens_used = response.usage.total_tokens if response.usage else None

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            data = {"translated_text": raw_content}

        return TranslationResult(
            translated_text=data.get("translated_text", ""),
            confidence_score=float(data.get("confidence_score", 0.90)),
            alternative_translations=data.get("alternative_translations", []),
            translator_notes=data.get("notes"),
            tokens_used=tokens_used,
            model_used=self.model,
        )
