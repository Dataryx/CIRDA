"""Health endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from cirda_api import __version__
from cirda_api.api.dependencies import ContainerDep
from cirda_api.api.v1.schemas.common import HealthResponse, ReadinessResponse
from cirda_api.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness(container: ContainerDep) -> ReadinessResponse:
    settings = get_settings()
    db_status = "memory" if settings.use_memory_store else ("configured" if settings.database_url else "sqlite")
    return ReadinessResponse(status="ready", database=db_status, redis=settings.event_bus)
