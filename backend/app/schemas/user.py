from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from app.schemas.common import AppBaseModel


# ── Request Schemas ────────────────────────────────────────────────────────────

class UserRegisterRequest(AppBaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[str] = Field("user", description="User role, e.g., 'user', 'admin'")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["user", "admin"]:
            raise ValueError("Role must be 'user' or 'admin'")
        return v


class UserLoginRequest(AppBaseModel):
    email: EmailStr
    password: str


class UserUpdateRequest(AppBaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    preferred_model: Optional[str] = None
    preferred_theme: Optional[str] = None
    preferred_tone: Optional[str] = None
    default_source_lang: Optional[str] = None
    default_target_lang: Optional[str] = None


class PasswordChangeRequest(AppBaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class TokenRefreshRequest(AppBaseModel):
    refresh_token: str


# ── Response Schemas ───────────────────────────────────────────────────────────

class UserResponse(AppBaseModel):
    id: uuid.UUID
    email: str
    username: str
    role: str
    is_active: bool
    is_verified: bool
    preferred_model: str
    preferred_theme: str
    preferred_tone: str
    default_source_lang: str
    default_target_lang: str
    created_at: datetime


class TokenResponse(AppBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(AppBaseModel):
    message: str


class UsageStatsResponse(AppBaseModel):
    total_translations: int
    total_documents: int
    total_characters_translated: int
    most_used_model: Optional[str] = None
    most_used_language_pair: Optional[str] = None
    translations_this_month: int
