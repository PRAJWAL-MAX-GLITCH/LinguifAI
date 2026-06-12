from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory sliding-window store: { ip: [timestamps] }
# For production, replace with a Redis-backed implementation using slowapi
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request/response with timing and a unique request ID.
    Adds X-Request-ID and X-Process-Time-Ms response headers.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Attach request_id to request state for downstream use
        request.state.request_id = request_id

        logger.info(
            "→ %s %s | client=%s | request_id=%s",
            request.method,
            request.url.path,
            request.client.host if request.client else "unknown",
            request_id,
        )

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "← %s %s | status=%d | duration=%.2fms | request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        return response


import redis.asyncio as redis
from app.core.config import settings

# Initialize Redis client (used globally by middleware)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Fixed-window rate limiter (per IP address) backed by Redis.
    Limits: RATE_LIMIT_PER_MINUTE requests per 60-second window.
    Exempted paths: /, /health, /docs, /redoc, /openapi.json
    """

    EXEMPT_PATHS: frozenset[str] = frozenset(
        {"/", "/health", "/docs", "/redoc", "/openapi.json"}
    )

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        limit = settings.RATE_LIMIT_PER_MINUTE
        window_seconds = 60

        current_minute = int(time.time() / window_seconds)
        redis_key = f"rate_limit:{client_ip}:{current_minute}"

        try:
            # Atomic INCR and EXPIRE using pipeline
            async with redis_client.pipeline(transaction=True) as pipe:
                pipe.incr(redis_key)
                pipe.expire(redis_key, window_seconds)
                results = await pipe.execute()
                request_count = results[0]

            if request_count > limit:
                logger.warning(
                    "Rate limit exceeded | ip=%s | count=%d | limit=%d",
                    client_ip,
                    request_count,
                    limit,
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Rate limit exceeded. Please try again in a minute.",
                        "limit": limit,
                        "window": "60 seconds",
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )
            
            response = await call_next(request)
            remaining = max(0, limit - request_count)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response

        except Exception as e:
            logger.error("Rate limiter Redis error: %s", str(e))
            # Fallback to allow request if Redis is down
            return await call_next(request)
