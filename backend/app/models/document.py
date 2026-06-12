from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User

# Document processing status values
DOCUMENT_STATUS_PENDING = "pending"
DOCUMENT_STATUS_PROCESSING = "processing"
DOCUMENT_STATUS_COMPLETED = "completed"
DOCUMENT_STATUS_FAILED = "failed"

# Supported file types
ALLOWED_FILE_TYPES = ("pdf", "docx", "txt", "srt")


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File metadata
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Translation settings
    source_language: Mapped[str] = mapped_column(String(10), nullable=False)
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)
    tone: Mapped[str] = mapped_column(String(20), default="formal", nullable=False)
    ai_model: Mapped[str] = mapped_column(String(50), nullable=False)

    # Processing state
    status: Mapped[str] = mapped_column(
        String(20), default=DOCUMENT_STATUS_PENDING, nullable=False, index=True
    )
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Output
    translated_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="documents")

    def __repr__(self) -> str:
        return (
            f"<Document id={self.id} "
            f"file={self.original_filename} "
            f"status={self.status}>"
        )
