import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware
from app.db.init_db import init_db
from app.db.session import engine

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("Starting AI Language Translation API v%s", settings.APP_VERSION)
    logger.info("=" * 60)
    await init_db()
    logger.info("Database tables initialized successfully.")
    yield
    logger.info("Shutting down AI Language Translation API...")
    await engine.dispose()
    logger.info("Database connections closed. Goodbye.")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "## AI-Powered Language Translation API\n\n"
        "Supports text translation, document translation, speech-to-text, "
        "translation history, and multi-model AI providers (GPT-4o, Gemini, DeepSeek).\n\n"
        "### Features\n"
        "- 🌐 100+ language pairs\n"
        "- 🤖 Multi-model AI support\n"
        "- 📄 Document translation (PDF, DOCX, TXT)\n"
        "- 🎙️ Speech-to-text via Whisper\n"
        "- 📊 Translation history & analytics\n"
        "- 🔐 JWT authentication\n"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time-Ms", "X-Request-ID"],
)

# ── Custom middleware (order matters — last added = first executed) ─────────────
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# ── Global Exception Handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled Exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


# ── API Routers ────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ── Root & Health endpoints ────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Root")
async def root():
    return {
        "status": "ok",
        "message": "AI Language Translation API is running",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"], summary="Health Check")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production",
    }
