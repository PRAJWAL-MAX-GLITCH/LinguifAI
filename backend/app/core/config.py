from __future__ import annotations

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Language Translation Tool"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ───────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-use-a-strong-random-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/translator_db"

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600          # 1 hour (default translation cache)
    REDIS_LANGUAGE_TTL: int = 86400      # 24 hours (language list cache)

    # ── CORS ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── AI Providers ───────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""          # Free alternative — https://console.groq.com/keys
    DEFAULT_AI_MODEL: str = "gemini-1.5-pro"  # Default to Gemini (free tier)

    # ── Translation Limits ─────────────────────────────────────────────────────
    MAX_TRANSLATION_LENGTH: int = 5000
    MAX_BATCH_SIZE: int = 10
    TRANSLATION_CHUNK_SIZE: int = 3000   # chars per chunk for document translation

    # ── Celery (Async Tasks) ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── File Storage ───────────────────────────────────────────────────────────
    FILE_STORAGE_PATH: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt", "srt"]

    # ── Rate Limiting ──────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    # ── Whisper / TTS ─────────────────────────────────────────────────────────
    WHISPER_MODEL: str = "whisper-1"     # OpenAI Whisper API model
    TTS_MODEL: str = "tts-1"
    TTS_VOICE: str = "alloy"


settings = Settings()
