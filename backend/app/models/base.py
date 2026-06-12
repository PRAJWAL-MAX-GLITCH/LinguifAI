from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 declarative base.
    All ORM models inherit from this class.
    """
    pass


class UUIDMixin:
    """
    Adds a UUID primary key column named 'id'.
    Uses PostgreSQL native UUID type (as_uuid=True returns Python uuid.UUID objects).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )


class TimestampMixin:
    """
    Adds created_at and updated_at timestamp columns.

    - created_at: set automatically on INSERT via server_default
    - updated_at: updated automatically on every UPDATE via onupdate
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
