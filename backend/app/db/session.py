from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Async Engine ───────────────────────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,        # Logs all SQL when DEBUG=True
    pool_pre_ping=True,         # Verify connection health before use
    pool_size=10,               # Number of persistent connections
    max_overflow=20,            # Extra connections beyond pool_size
    pool_recycle=3600,          # Recycle connections every 1 hour
    pool_timeout=30,            # Wait up to 30s for a connection from pool
)

# ── Session Factory ────────────────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # Avoid lazy-load errors after commit
    autoflush=False,
    autocommit=False,
)


# ── Dependency: get_db ────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.

    Automatically commits on success and rolls back on exception.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.error("Database session rolled back due to exception: %s", exc)
            raise
        finally:
            await session.close()
