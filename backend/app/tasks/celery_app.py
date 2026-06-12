from celery import Celery
from celery.signals import worker_ready, worker_shutdown

from app.core.config import settings

# ── Celery Application ─────────────────────────────────────────────────────────

celery_app = Celery(
    "linguifai_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.document_tasks"],
)

# ── Configuration ──────────────────────────────────────────────────────────────

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task behaviour
    task_track_started=True,          # Mark tasks as STARTED (visible in result backend)
    task_acks_late=True,               # Acknowledge AFTER task completes (safer for retries)
    task_reject_on_worker_lost=True,   # Re-queue if worker dies mid-task
    worker_prefetch_multiplier=1,      # Fetch one task at a time (fair for long-running tasks)

    # Result expiry
    result_expires=3600 * 24,          # Keep results for 24 hours

    # Time limits
    task_soft_time_limit=1800,         # Soft kill after 30 min  (SoftTimeLimitExceeded)
    task_time_limit=3600,              # Hard kill after 60 min

    # Retry defaults
    task_max_retries=2,
    task_default_retry_delay=30,

    # Queue routing
    task_routes={
        "app.tasks.document_tasks.process_document_task": {"queue": "documents"},
    },

    # Worker concurrency and pool
    worker_concurrency=2,
)

# ── Signal Handlers ────────────────────────────────────────────────────────────

@worker_ready.connect
def on_worker_ready(sender, **kwargs):
    import logging
    logging.getLogger(__name__).info(
        "Celery worker ready | broker=%s", settings.CELERY_BROKER_URL
    )


@worker_shutdown.connect
def on_worker_shutdown(sender, **kwargs):
    import logging
    logging.getLogger(__name__).info("Celery worker shutting down.")
