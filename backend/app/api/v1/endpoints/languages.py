from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.utils.language_codes import LANGUAGES

router = APIRouter()

logger = logging.getLogger(__name__)


class LanguageInfo(BaseModel):
    code: str
    name: str
    native_name: str


@router.get(
    "",
    response_model=list[LanguageInfo],
    summary="List all supported languages",
)
async def list_languages():
    """Returns a list of all 100+ supported languages for translation."""
    return [
        LanguageInfo(code=code, name=data["name"], native_name=data["nativeName"])
        for code, data in LANGUAGES.items()
    ]


@router.get(
    "/{code}",
    response_model=LanguageInfo,
    summary="Get language by code",
)
async def get_language(code: str):
    """Get details for a specific ISO 639-1 language code."""
    data = LANGUAGES.get(code.lower())
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Language code '{code}' not supported.",
        )
    return LanguageInfo(code=code.lower(), name=data["name"], native_name=data["nativeName"])
