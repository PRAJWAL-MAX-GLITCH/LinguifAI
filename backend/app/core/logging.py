from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging() -> None:
    """
    Configure application-wide logging.

    - Console handler: human-readable, colored-ready format
    - File handler: rotating, UTF-8, stored in ./logs/app.log
    - Suppresses noisy third-party loggers
    """
    # Determine log level (import here to avoid circular imports)
    from app.core.config import settings

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # ── Formatters ─────────────────────────────────────────────────────────────
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    # ── Root Logger ────────────────────────────────────────────────────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear any pre-existing handlers (e.g., from uvicorn boot)
    root_logger.handlers.clear()

    # ── Console Handler ────────────────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # ── Rotating File Handler ──────────────────────────────────────────────────
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        filename="logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB per file
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # ── Suppress Noisy Third-Party Loggers ────────────────────────────────────
    _silence = [
        "httpx",
        "httpcore",
        "openai",
        "google",
        "sqlalchemy.engine",
        "sqlalchemy.pool",
        "uvicorn.access",
        "celery",
        "kombu",
    ]
    for logger_name in _silence:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # ── Confirm setup ─────────────────────────────────────────────────────────
    _logger = logging.getLogger(__name__)
    _logger.info(
        "Logging initialized | level=%s | file=logs/app.log",
        logging.getLevelName(log_level),
    )
