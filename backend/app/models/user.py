from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.translation import Translation
    from app.models.document import Document
    from app.models.usage_log import UsageLog


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role-ready architecture
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # User preferences
    preferred_model: Mapped[str] = mapped_column(
        String(50), default="gpt-4o", nullable=False
    )
    preferred_theme: Mapped[str] = mapped_column(
        String(20), default="dark", nullable=False
    )
    preferred_tone: Mapped[str] = mapped_column(
        String(20), default="formal", nullable=False
    )
    default_source_lang: Mapped[str] = mapped_column(
        String(10), default="auto", nullable=False
    )
    default_target_lang: Mapped[str] = mapped_column(
        String(10), default="en", nullable=False
    )

    # Relationships
    translations: Mapped[list["Translation"]] = relationship(
        "Translation", back_populates="user", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    usage_logs: Mapped[list["UsageLog"]] = relationship(
        "UsageLog", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
