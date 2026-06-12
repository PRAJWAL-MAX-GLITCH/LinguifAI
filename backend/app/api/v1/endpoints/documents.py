from __future__ import annotations

import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.db.session import get_db
from app.models.document import DOCUMENT_STATUS_COMPLETED
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.document import DocumentListResponse, DocumentResponse, DocumentUploadRequest
from app.services.document_service import DocumentService
from app.tasks.document_tasks import process_document_task

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a document for translation",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF, DOCX, or TXT file"),
    source_language: str = Form(default="auto"),
    target_language: str = Form(...),
    tone: str = Form(default="formal"),
    model: str = Form(default="gpt-4o"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a document for asynchronous background translation.

    Returns immediately with document ID and status **pending**.
    Poll `GET /documents/{id}` to monitor translation progress.
    """
    upload_request = DocumentUploadRequest(
        source_language=source_language,
        target_language=target_language,
        tone=tone,
        model=model,
    )
    service = DocumentService(db)
    document = await service.create_document(file, upload_request, current_user.id)

    # Enqueue the Celery translation task in the background
    process_document_task.delay(str(document.id))

    return document


@router.get(
    "",
    response_model=List[DocumentListResponse],
    summary="List all user documents",
)
async def list_documents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all documents uploaded by the current user, newest first."""
    service = DocumentService(db)
    docs = await service.list_documents(current_user.id)
    return docs


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Get document status and metadata",
)
async def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Poll this endpoint to track translation progress.
    Status values: **pending** → **processing** → **completed** | **failed**
    """
    service = DocumentService(db)
    doc = await service.get_by_id(doc_id, current_user.id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return doc


@router.get(
    "/{doc_id}/download",
    summary="Download the translated document",
)
async def download_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Download the translated file once processing is **completed**.
    Returns the file as an attachment.
    """
    service = DocumentService(db)
    doc = await service.get_by_id(doc_id, current_user.id)

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    if doc.status != DOCUMENT_STATUS_COMPLETED or not doc.translated_filename:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document is not ready for download. Current status: '{doc.status}'",
        )

    # Resolve output file path (could be .docx if original was PDF)
    base = Path(doc.translated_filename)
    for candidate in [base, base.with_suffix(".docx"), base.with_suffix(".txt")]:
        file_path = Path(settings.FILE_STORAGE_PATH) / "translated" / candidate
        if file_path.exists():
            download_name = f"translated_{doc.original_filename}"
            # Match extension of the actual output file
            download_name = Path(download_name).with_suffix(candidate.suffix).name
            return FileResponse(
                path=str(file_path),
                filename=download_name,
                media_type="application/octet-stream",
                headers={"Content-Disposition": f'attachment; filename="{download_name}"'},
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Translated file not found on disk.",
    )


@router.delete(
    "/{doc_id}",
    response_model=MessageResponse,
    summary="Delete a document and its files",
)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Permanently deletes the document record and its associated files from disk."""
    service = DocumentService(db)
    deleted = await service.delete_document(doc_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return MessageResponse(message="Document and associated files deleted successfully.")
