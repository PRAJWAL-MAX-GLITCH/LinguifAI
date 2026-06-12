from __future__ import annotations

import logging

from sqlalchemy import text

from app.db.session import engine
from app.models.base import Base

# Import all models so SQLAlchemy registers them with Base.metadata
from app.models.user import User  # noqa: F401
from app.models.translation import Translation  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.usage_log import UsageLog  # noqa: F401

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    Create all database tables if they do not exist.

    This is used at application startup via the FastAPI lifespan event.
    For production migrations, use Alembic instead of create_all().
    """
    async with engine.begin() as conn:
        logger.info("Running database initialization...")

        # Verify connection is alive
        await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified.")

        # Create all tables registered with Base.metadata
        await conn.run_sync(Base.metadata.create_all)
        logger.info(
            "Tables created/verified: %s",
            list(Base.metadata.tables.keys()),
        )
