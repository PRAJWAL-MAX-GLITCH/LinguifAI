from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from app.schemas.common import AppBaseModel


# ── Response Schemas ───────────────────────────────────────────────────────────

class UsageLogResponse(AppBaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    endpoint: str
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None
    status_code: int
    created_at: datetime
