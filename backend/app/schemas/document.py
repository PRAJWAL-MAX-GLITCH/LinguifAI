from __future__ import annotations

import uuid
from typing import List, Optional
from datetime import datetime

from app.schemas.common import AppBaseModel


# ── Upload Request (from multipart form) ──────────────────────────────────────

class DocumentUploadRequest(AppBaseModel):
    source_language: str = "auto"
    target_language: str
    tone: str = "formal"
    model: str = "gpt-4o"


# ── Response Schemas ───────────────────────────────────────────────────────────

class DocumentResponse(AppBaseModel):
    id: uuid.UUID
    original_filename: str
    file_type: str
    file_size_bytes: int
    source_language: Optional[str] = None
    target_language: str
    tone: str
    ai_model: str
    status: str
    error_message: Optional[str] = None
    translated_filename: Optional[str] = None
    char_count: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class DocumentListResponse(AppBaseModel):
    id: uuid.UUID
    original_filename: str
    file_type: str
    file_size_bytes: int
    source_language: Optional[str] = None
    target_language: str
    ai_model: str
    status: str
    created_at: datetime
