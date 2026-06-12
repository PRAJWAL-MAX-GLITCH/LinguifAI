from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.translation import TranslationListResponse
from app.services.history_service import HistoryService

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse[TranslationListResponse],
    summary="Get translation history",
)
async def get_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    source_lang: Optional[str] = Query(default=None),
    target_lang: Optional[str] = Query(default=None),
    starred: Optional[bool] = Query(default=None),
    q: Optional[str] = Query(default=None, description="Search in source/translated text"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns paginated translation history with optional filters."""
    service = HistoryService(db)
    return await service.get_history(
        user_id=current_user.id,
        page=page,
        limit=limit,
        source_lang=source_lang,
        target_lang=target_lang,
        starred=starred,
        search=q,
    )


@router.get(
    "/{translation_id}",
    response_model=TranslationListResponse,
    summary="Get single translation",
)
async def get_translation(
    translation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    translation = await service.get_by_id(translation_id, current_user.id)
    if not translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found.")
    return translation


@router.delete(
    "",
    response_model=MessageResponse,
    summary="Clear all translation history",
)
async def clear_history(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    count = await service.clear_all(current_user.id)
    return MessageResponse(message=f"Deleted {count} translation(s).")


@router.delete(
    "/{translation_id}",
    response_model=MessageResponse,
    summary="Delete a single translation",
)
async def delete_translation(
    translation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    deleted = await service.delete_by_id(translation_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found.")
    return MessageResponse(message="Translation deleted.")


@router.patch(
    "/{translation_id}/star",
    summary="Toggle star on a translation",
)
async def toggle_star(
    translation_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = HistoryService(db)
    new_star_state = await service.toggle_star(translation_id, current_user.id)
    if new_star_state is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found.")
    return {"id": translation_id, "is_starred": new_star_state}
