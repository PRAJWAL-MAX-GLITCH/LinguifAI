from __future__ import annotations

import logging
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global async Redis client
redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """Get or initialize the global Redis connection pool."""
    global redis_client
    if redis_client is None:
        logger.info("Initializing Redis connection to %s", settings.REDIS_URL)
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,  # Return strings instead of bytes
        )
    return redis_client


async def get_cached(key: str) -> Optional[str]:
    """Retrieve a value from the Redis cache."""
    try:
        redis = await get_redis()
        return await redis.get(key)
    except Exception as e:
        logger.error("Redis get error for key %s: %s", key, e)
        return None


async def set_cached(key: str, value: str, ttl: int = 3600) -> bool:
    """Set a value in the Redis cache with an expiration (TTL in seconds)."""
    try:
        redis = await get_redis()
        await redis.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error("Redis set error for key %s: %s", key, e)
        return False


async def delete_cached(key: str) -> bool:
    """Delete a key from the Redis cache."""
    try:
        redis = await get_redis()
        await redis.delete(key)
        return True
    except Exception as e:
        logger.error("Redis delete error for key %s: %s", key, e)
        return False
