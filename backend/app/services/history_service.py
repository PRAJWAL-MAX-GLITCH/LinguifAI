from __future__ import annotations

import logging
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.translation import Translation
from app.schemas.common import PaginatedResponse
from app.schemas.translation import TranslationListResponse

logger = logging.getLogger(__name__)


class HistoryService:
    """Business logic for translation history management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_history(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        limit: int = 20,
        source_lang: Optional[str] = None,
        target_lang: Optional[str] = None,
        starred: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[TranslationListResponse]:
        filters = [Translation.user_id == user_id]

        if source_lang:
            filters.append(Translation.source_language == source_lang)
        if target_lang:
            filters.append(Translation.target_language == target_lang)
        if starred is not None:
            filters.append(Translation.is_starred == starred)
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    Translation.source_text.ilike(search_term),
                    Translation.translated_text.ilike(search_term),
                )
            )

        # Count total
        count_stmt = select(func.count()).where(and_(*filters))
        total = (await self.db.execute(count_stmt)).scalar_one()

        # Fetch page
        offset = (page - 1) * limit
        stmt = (
            select(Translation)
            .where(and_(*filters))
            .order_by(Translation.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        translations = result.scalars().all()

        items = [self._to_list_response(t) for t in translations]
        return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)

    async def get_by_id(
        self, translation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Translation]:
        stmt = select(Translation).where(
            and_(Translation.id == translation_id, Translation.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id(
        self, translation_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        stmt = delete(Translation).where(
            and_(Translation.id == translation_id, Translation.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def clear_all(self, user_id: uuid.UUID) -> int:
        stmt = delete(Translation).where(Translation.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.rowcount

    async def toggle_star(
        self, translation_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[bool]:
        translation = await self.get_by_id(translation_id, user_id)
        if not translation:
            return None
        translation.is_starred = not translation.is_starred
        await self.db.flush()
        return translation.is_starred

    def _to_list_response(self, t: Translation) -> TranslationListResponse:
        return TranslationListResponse(
            id=t.id,
            source_language=t.source_language,
            target_language=t.target_language,
            source_text=t.source_text,
            translated_text=t.translated_text,
            ai_model=t.ai_model,
            tone=t.tone,
            confidence_score=t.confidence_score,
            is_starred=t.is_starred,
            char_count=t.char_count,
            created_at=t.created_at,
        )
