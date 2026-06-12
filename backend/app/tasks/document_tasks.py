from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from pathlib import Path
from typing import List

from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.document import (
    DOCUMENT_STATUS_COMPLETED,
    DOCUMENT_STATUS_FAILED,
    DOCUMENT_STATUS_PROCESSING,
    Document,
)
from app.services.ai.base_provider import TranslationRequest as AITranslationRequest
from app.services.ai.provider_factory import ProviderFactory
from app.tasks.celery_app import celery_app
from app.utils.document_parser import (
    build_translated_output,
    chunk_text,
    extract_text,
)

logger = get_task_logger(__name__)


# ── Step Helpers ───────────────────────────────────────────────────────────────

async def _load_document(doc_id: str) -> tuple[Document, "AsyncSession"]:  # noqa: F821
    """Open a fresh DB session and load the Document record by ID."""
    db = AsyncSessionLocal()
    stmt = select(Document).where(Document.id == uuid.UUID(doc_id))
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    return doc, db


async def _mark_processing(db, doc: Document) -> None:
    """Transition document to PROCESSING state."""
    doc.status = DOCUMENT_STATUS_PROCESSING
    await db.commit()
    logger.info("[%s] Status → processing", doc.id)


async def _translate_chunks(
    chunks: List[str],
    doc: Document,
) -> List[str]:
    """
    Translate each text chunk sequentially using the document's AI model.
    Tracks per-chunk timing for diagnostics.
    """
    provider = ProviderFactory.get_provider(doc.ai_model)
    translated: List[str] = []
    total = len(chunks)

    for idx, chunk in enumerate(chunks, 1):
        chunk_start = time.perf_counter()
        logger.info("[%s] Translating chunk %d / %d …", doc.id, idx, total)

        ai_req = AITranslationRequest(
            source_text=chunk,
            source_language=doc.source_language or "auto",
            target_language=doc.target_language,
            tone=doc.tone or "formal",
        )
        result = await provider.translate(ai_req)
        translated.append(result.translated_text)

        elapsed = int((time.perf_counter() - chunk_start) * 1000)
        logger.info(
            "[%s] Chunk %d done in %dms | confidence=%.2f",
            doc.id,
            idx,
            elapsed,
            result.confidence_score,
        )

    return translated


async def _save_output(translated_chunks: List[str], doc: Document) -> str:
    """
    Reassemble chunks into a single translated document and persist to disk.
    Returns the stored filename.
    """
    full_translation = "\n\n".join(translated_chunks)

    translated_filename = f"translated_{doc.stored_filename}"
    output_dir = Path(settings.FILE_STORAGE_PATH) / "translated"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / translated_filename

    build_translated_output(full_translation, output_path, doc.file_type)
    logger.info("[%s] Output written → %s", doc.id, output_path)

    return translated_filename


async def _mark_completed(db, doc: Document, translated_filename: str, char_count: int) -> None:
    """Mark the document as COMPLETED and store output metadata."""
    doc.status = DOCUMENT_STATUS_COMPLETED
    doc.translated_filename = translated_filename
    doc.char_count = char_count
    await db.commit()
    logger.info("[%s] Status → completed ✓", doc.id)


async def _mark_failed(db, doc: Document, error: str) -> None:
    """Mark the document as FAILED and persist the error message."""
    try:
        doc.status = DOCUMENT_STATUS_FAILED
        doc.error_message = str(error)[:500]
        await db.commit()
        logger.error("[%s] Status → failed | reason: %s", doc.id, error)
    except Exception as db_err:
        logger.critical("[%s] Could not mark as failed in DB: %s", doc.id, db_err)


# ── Main Async Pipeline ────────────────────────────────────────────────────────

async def run_document_translation_pipeline(doc_id: str) -> dict:
    """
    Complete document translation pipeline:

    1. Load document from DB
    2. Mark as PROCESSING
    3. Extract text from file (PDF / DOCX / TXT)
    4. Split into smart chunks
    5. Translate each chunk via AI provider
    6. Reassemble and write output file
    7. Mark as COMPLETED
    """
    pipeline_start = time.perf_counter()
    doc = None
    db = None

    try:
        # ── Step 1: Load ───────────────────────────────────────────────────────
        doc, db = await _load_document(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found in database.")

        logger.info(
            "[%s] Pipeline START | file=%s | model=%s | %s → %s",
            doc.id,
            doc.original_filename,
            doc.ai_model,
            doc.source_language,
            doc.target_language,
        )

        # ── Step 2: Mark Processing ────────────────────────────────────────────
        await _mark_processing(db, doc)

        # ── Step 3: Extract Text ───────────────────────────────────────────────
        original_path = (
            Path(settings.FILE_STORAGE_PATH) / "originals" / doc.stored_filename
        )
        if not original_path.exists():
            raise FileNotFoundError(f"Source file missing: {original_path}")

        full_text = extract_text(original_path, doc.file_type)
        char_count = len(full_text)
        logger.info("[%s] Extracted %d characters.", doc.id, char_count)

        # ── Step 4: Chunk ──────────────────────────────────────────────────────
        chunks = chunk_text(full_text)
        logger.info("[%s] Created %d chunks.", doc.id, len(chunks))

        # ── Step 5: Translate ──────────────────────────────────────────────────
        translated_chunks = await _translate_chunks(chunks, doc)

        # ── Step 6: Write Output ───────────────────────────────────────────────
        translated_filename = await _save_output(translated_chunks, doc)

        # ── Step 7: Mark Completed ─────────────────────────────────────────────
        await _mark_completed(db, doc, translated_filename, char_count)

        total_elapsed = int((time.perf_counter() - pipeline_start) * 1000)
        logger.info(
            "[%s] Pipeline COMPLETE in %dms | chunks=%d | chars=%d",
            doc.id,
            total_elapsed,
            len(chunks),
            char_count,
        )

        return {
            "doc_id": doc_id,
            "status": "completed",
            "chunks": len(chunks),
            "char_count": char_count,
            "elapsed_ms": total_elapsed,
            "output_file": translated_filename,
        }

    except SoftTimeLimitExceeded:
        logger.error("[%s] Task soft time limit exceeded!", doc_id)
        if doc and db:
            await _mark_failed(db, doc, "Task timed out (soft limit exceeded).")
        raise

    except Exception as exc:
        logger.exception("[%s] Pipeline FAILED: %s", doc_id, exc)
        if doc and db:
            await _mark_failed(db, doc, str(exc))
        raise

    finally:
        if db:
            await db.close()


# ── Celery Task Entrypoint ─────────────────────────────────────────────────────

@celery_app.task(
    bind=True,
    name="app.tasks.document_tasks.process_document_task",
    max_retries=2,
    default_retry_delay=30,
    queue="documents",
    acks_late=True,
)
def process_document_task(self, doc_id: str) -> dict:
    """
    Celery task: translate an uploaded document end-to-end.

    Args:
        doc_id: UUID string of the Document record.

    Returns:
        Summary dict with status, chunk count, and elapsed time.

    Retries:
        Up to 2 times with a 30-second delay on unexpected failures.
        Does NOT retry on FileNotFoundError or ValueError (data issues).
    """
    logger.info("Task received | doc_id=%s | attempt=%d", doc_id, self.request.retries + 1)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            run_document_translation_pipeline(doc_id)
        )
        return result
    except (FileNotFoundError, ValueError) as exc:
        # Non-retryable errors (bad input data)
        logger.error("Non-retryable error for doc %s: %s", doc_id, exc)
        return {"doc_id": doc_id, "status": "failed", "error": str(exc)}
    except Exception as exc:
        logger.warning(
            "Retrying doc %s (attempt %d) after error: %s",
            doc_id,
            self.request.retries + 1,
            exc,
        )
        raise self.retry(exc=exc, countdown=30)
    finally:
        loop.close()
