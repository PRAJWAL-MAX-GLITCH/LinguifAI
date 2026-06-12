from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.translation import (
    BatchTranslationRequest,
    DetectLanguageRequest,
    DetectLanguageResponse,
    TranslationRequest,
    TranslationResponse,
)
from app.services.ai.provider_factory import ProviderFactory
from app.services.translation_service import TranslationService
from app.utils.language_codes import detect_language, get_language_name

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate text",
)
async def translate_text(
    request: TranslationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Translate text from source language to target language using the specified AI model.

    - **source_language**: ISO 639-1 code or 'auto' for detection
    - **target_language**: ISO 639-1 code (required)
    - **tone**: casual | formal | technical | literary
    - **model**: gpt-4o | gpt-4o-mini | gemini-1.5-pro | deepseek-chat
    """
    # Validation: target language cannot be auto
    if request.target_language.lower() == "auto":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_language cannot be 'auto'. You must specify a valid ISO 639-1 code.",
        )

    # Validation: source and target cannot be identical (unless auto)
    if (
        request.source_language.lower() != "auto"
        and request.source_language.lower() == request.target_language.lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_language and target_language cannot be the same.",
        )

    try:
        service = TranslationService(db)
        return await service.translate(request, user_id=current_user.id)
    except ValueError as e:
        # e.g., ProviderFactory throws ValueError for unsupported models
        logger.warning("Translation validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Translation processing failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the translation. Please try again later.",
        )


@router.post(
    "/batch",
    response_model=List[TranslationResponse],
    status_code=status.HTTP_200_OK,
    summary="Batch translate multiple texts",
)
async def batch_translate(
    request: BatchTranslationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Translate up to 10 texts in parallel.
    Useful for translating arrays of strings in an interface or short document chunks.
    """
    if not request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch request must contain at least one item.",
        )

    for i, item in enumerate(request.items):
        if item.target_language.lower() == "auto":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item at index {i} has invalid target_language 'auto'.",
            )

    try:
        service = TranslationService(db)
        results = await service.batch_translate(request.items, user_id=current_user.id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Batch translation processing failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch translation failed. Please verify inputs and try again.",
        )


@router.post(
    "/detect",
    response_model=DetectLanguageResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect language of text",
)
async def detect_text_language(
    request: DetectLanguageRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Auto-detect the language of the provided text.
    Returns the ISO 639-1 code and the human-readable language name.
    """
    try:
        detected_code = detect_language(request.text)
        language_name = get_language_name(detected_code)
        
        return DetectLanguageResponse(
            detected_language=detected_code,
            language_name=language_name,
            confidence=0.95,  # langdetect is mostly deterministic, mock confidence for API consistency
        )
    except Exception as e:
        logger.error("Language detection failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect language from text.",
        )


@router.get(
    "/models",
    summary="List available AI models",
)
async def list_models(
    current_user: User = Depends(get_current_active_user),
):
    """
    Returns all currently supported AI translation models.
    Use this to populate frontend model-selection dropdowns.
    """
    try:
        models = ProviderFactory.available_models()
        return {"models": models}
    except Exception as e:
        logger.error("Failed to list models: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve available AI models.",
        )
