from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Translation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "translations"

    # Foreign key
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Translation data
    # Translation data
    source_language: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    target_language: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)

    # AI metadata
    tone: Mapped[str] = mapped_column(String(20), default="formal", nullable=False)
    ai_model: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Alternative translations stored as JSON text
    alternative_translations: Mapped[str | None] = mapped_column(Text, nullable=True)
    translator_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User interaction
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)

    # Stats
    char_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="translations")

    def __repr__(self) -> str:
        return (
            f"<Translation id={self.id} "
            f"{self.source_language}→{self.target_language} "
            f"model={self.ai_model}>"
        )
