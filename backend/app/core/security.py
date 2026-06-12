from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password Utilities ─────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Utilities ──────────────────────────────────────────────────────────────

def create_access_token(
    subject: str | Any,
    role: str = "user",
    expires_delta: timedelta | None = None,
) -> str:
    """Create a short-lived JWT access token with role embedded."""
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | Any, role: str = "user") -> str:
    """Create a long-lived JWT refresh token with role embedded."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Returns the payload dict on success, or an empty dict if invalid/expired.
    """
    try:
        payload: dict = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return {}


def get_token_subject(token: str) -> str | None:
    """Extract the 'sub' field from a valid JWT, or None if invalid."""
    payload = decode_token(token)
    return payload.get("sub")

def get_token_role(token: str) -> str | None:
    """Extract the 'role' field from a valid JWT."""
    payload = decode_token(token)
    return payload.get("role")
