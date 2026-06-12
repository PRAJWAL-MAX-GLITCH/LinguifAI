from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.translation import Translation
from app.schemas.translation import TranslationRequest, TranslationResponse
from app.services.ai.base_provider import (
    TranslationRequest as AITranslationRequest,
)
from app.services.ai.provider_factory import ProviderFactory
from app.utils.cache import get_cached, set_cached
from app.utils.language_codes import detect_language

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Core business logic for text translation.

    Handles:
    - Auto language detection
    - Redis caching
    - AI provider routing via ProviderFactory
    - Saving results to translation history
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def translate(
        self,
        request: TranslationRequest,
        user_id: uuid.UUID,
    ) -> TranslationResponse:
        """
        Translates text with Redis caching, logs it in the database, and returns the response.
        """
        start_time = time.perf_counter()

        # 1. Auto Detect Language
        source_lang = request.source_language
        if source_lang.lower() == "auto":
            source_lang = detect_language(request.source_text)
            logger.info("Auto-detected source language: %s", source_lang)

        # 2. Build Cache Key
        cache_key = self._build_cache_key(
            text=request.source_text,
            source=source_lang,
            target=request.target_language,
            tone=request.tone,
            model=request.model,
        )

        # 3. Check Redis Cache
        cached_result = await get_cached(cache_key)
        
        if cached_result:
            # → Cache Hit Return
            logger.info("Cache HIT for translation key: %s", cache_key[:16])
            data = json.loads(cached_result)
            
            # Still save the translation history for this user
            translation = await self._save_translation(
                user_id=user_id,
                source_text=request.source_text,
                source_language=source_lang,
                target_language=request.target_language,
                translated_text=data["translated_text"],
                tone=request.tone,
                model=request.model,
                confidence_score=data.get("confidence_score"),
                alternatives=data.get("alternative_translations", []),
                notes=data.get("translator_notes"),
                latency_ms=0,  # 0 ms latency since it was an instant cache hit
                tokens_used=None,
            )
            return self._to_response(translation)

        # 4. Cache Miss — Call Selected Model
        logger.info("Cache MISS — calling AI provider: %s", request.model)
        provider = ProviderFactory.get_provider(request.model)

        ai_request = AITranslationRequest(
            source_text=request.source_text,
            source_language=source_lang,
            target_language=request.target_language,
            tone=request.tone,
            include_alternatives=request.include_alternatives,
        )

        ai_result = await provider.translate(ai_request)
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        
        logger.info(
            "Translation complete | model=%s | latency=%dms",
            request.model,
            latency_ms,
        )

        # 5. Store Result in Redis Cache
        cache_payload = json.dumps({
            "translated_text": ai_result.translated_text,
            "confidence_score": ai_result.confidence_score,
            "alternative_translations": ai_result.alternative_translations,
            "translator_notes": ai_result.translator_notes,
        })
        # TTL: 1 hour (3600 seconds)
        await set_cached(cache_key, cache_payload, ttl=3600)

        # 6. Save Translation History
        translation = await self._save_translation(
            user_id=user_id,
            source_text=request.source_text,
            source_language=source_lang,
            target_language=request.target_language,
            translated_text=ai_result.translated_text,
            tone=request.tone,
            model=request.model,
            confidence_score=ai_result.confidence_score,
            alternatives=ai_result.alternative_translations,
            notes=ai_result.translator_notes,
            latency_ms=latency_ms,
            tokens_used=ai_result.tokens_used,
        )

        return self._to_response(translation)

    async def batch_translate(
        self,
        requests: List[TranslationRequest],
        user_id: uuid.UUID,
    ) -> List[TranslationResponse]:
        """Process multiple translation requests concurrently."""
        import asyncio
        tasks = [self.translate(req, user_id) for req in requests]
        return await asyncio.gather(*tasks)

    # ── Internal Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _build_cache_key(
        text: str, source: str, target: str, tone: str, model: str
    ) -> str:
        """Create a deterministic SHA-256 hash key for caching translations."""
        raw_string = f"{text}|{source}|{target}|{tone}|{model}"
        hash_digest = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
        return f"translate:{hash_digest}"

    async def _save_translation(
        self,
        user_id: uuid.UUID,
        source_text: str,
        source_language: str,
        target_language: str,
        translated_text: str,
        tone: str,
        model: str,
        confidence_score: Optional[float],
        alternatives: List[str],
        notes: Optional[str],
        latency_ms: int,
        tokens_used: Optional[int],
    ) -> Translation:
        """Persist the translation result to the PostgreSQL database."""
        alts_json = json.dumps(alternatives) if alternatives else None

        translation = Translation(
            user_id=user_id,
            source_language=source_language,
            target_language=target_language,
            source_text=source_text,
            translated_text=translated_text,
            tone=tone,
            ai_model=model,
            confidence_score=confidence_score,
            alternative_translations=alts_json,
            translator_notes=notes,
            char_count=len(source_text),
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            is_starred=False,
        )
        self.db.add(translation)
        await self.db.flush()
        await self.db.refresh(translation)
        
        return translation

    def _to_response(self, translation: Translation) -> TranslationResponse:
        """Convert a Translation ORM model into a TranslationResponse schema."""
        alternatives = []
        if translation.alternative_translations:
            try:
                alternatives = json.loads(translation.alternative_translations)
            except (json.JSONDecodeError, TypeError):
                pass

        return TranslationResponse(
            id=translation.id,
            translated_text=translation.translated_text,
            source_language=translation.source_language,
            target_language=translation.target_language,
            confidence_score=translation.confidence_score,
            alternative_translations=alternatives,
            translator_notes=translation.translator_notes,
            latency_ms=translation.latency_ms,
            model_used=translation.ai_model,
            tone=translation.tone,
            is_starred=translation.is_starred,
            created_at=translation.created_at,
        )
