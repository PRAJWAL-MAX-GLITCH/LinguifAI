from fastapi import APIRouter

from app.api.v1.endpoints import (
    translation,
    history,
    documents,
    speech,
    languages,
    users,
)

api_router = APIRouter()

api_router.include_router(
    users.router,
    prefix="/auth",
    tags=["Authentication"],
)
api_router.include_router(
    translation.router,
    prefix="/translate",
    tags=["Translation"],
)
api_router.include_router(
    history.router,
    prefix="/history",
    tags=["History"],
)
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)
api_router.include_router(
    speech.router,
    prefix="/speech",
    tags=["Speech"],
)
api_router.include_router(
    languages.router,
    prefix="/languages",
    tags=["Languages"],
)
