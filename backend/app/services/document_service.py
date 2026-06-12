from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import (
    DOCUMENT_STATUS_FAILED,
    DOCUMENT_STATUS_PENDING,
    Document,
)
from app.schemas.document import DocumentUploadRequest

logger = logging.getLogger(__name__)

MAX_FILE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_TYPES = {"pdf", "docx", "txt"}


class DocumentService:
    """Business logic for document upload, storage, and retrieval."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_document(
        self,
        file: UploadFile,
        request: DocumentUploadRequest,
        user_id: uuid.UUID,
    ) -> Document:
        # Validate extension
        extension = self._get_extension(file.filename or "")
        if extension not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=(
                    f"File type '.{extension}' is not supported. "
                    f"Allowed types: {sorted(ALLOWED_TYPES)}"
                ),
            )

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the {settings.MAX_FILE_SIZE_MB} MB limit.",
            )
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        # Save original file to disk
        stored_filename = f"{uuid.uuid4()}.{extension}"
        storage_dir = Path(settings.FILE_STORAGE_PATH) / "originals"
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_path = storage_dir / stored_filename

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(
            "Stored uploaded file: %s (%d bytes) → %s",
            file.filename,
            len(content),
            file_path,
        )

        # Create DB record
        document = Document(
            user_id=user_id,
            original_filename=file.filename or stored_filename,
            stored_filename=stored_filename,
            file_type=extension,
            file_size_bytes=len(content),
            source_language=request.source_language,
            target_language=request.target_language,
            tone=request.tone,
            ai_model=request.model,
            status=DOCUMENT_STATUS_PENDING,
        )
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def get_by_id(
        self, doc_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Document]:
        stmt = select(Document).where(
            and_(Document.id == doc_id, Document.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_documents(self, user_id: uuid.UUID) -> List[Document]:
        stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_document(
        self, doc_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        doc = await self.get_by_id(doc_id, user_id)
        if not doc:
            return False

        # Remove files from disk
        for subdir, attr in [("originals", "stored_filename"), ("translated", "translated_filename")]:
            filename = getattr(doc, attr)
            if filename:
                file_path = Path(settings.FILE_STORAGE_PATH) / subdir / filename
                if file_path.exists():
                    file_path.unlink()
                    logger.info("Deleted file: %s", file_path)

        await self.db.delete(doc)
        return True

    @staticmethod
    def _get_extension(filename: str) -> str:
        suffix = Path(filename).suffix.lstrip(".").lower()
        return suffix or "unknown"
