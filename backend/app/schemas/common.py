from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ── Base Schema ────────────────────────────────────────────────────────────────

class AppBaseModel(BaseModel):
    """Base model with ORM mode enabled for all schemas."""
    model_config = ConfigDict(from_attributes=True)


# ── Pagination ─────────────────────────────────────────────────────────────────

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(AppBaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        limit: int,
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=-(-total // limit),  # ceiling division
        )


# ── Responses ─────────────────────────────────────────────────────────────────

class MessageResponse(AppBaseModel):
    message: str


class ErrorResponse(AppBaseModel):
    detail: str
    code: Optional[str] = None


class HealthResponse(AppBaseModel):
    status: str
    version: str
    environment: str
