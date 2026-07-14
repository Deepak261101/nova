"""Health/readiness endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.api.deps import get_session
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "nova-backend", "version": get_settings().env}


@router.get("/ready")
async def ready(session: Annotated[object, Depends(get_session)]) -> dict[str, str]:
    # Touch the DB to confirm connectivity.
    await session.execute(text("SELECT 1"))  # type: ignore[attr-defined]
    return {"status": "ready"}
