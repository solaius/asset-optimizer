"""Health check routes."""

from __future__ import annotations

from fastapi import APIRouter

from asset_optimizer import __version__
from asset_optimizer.api.schemas import HealthResponse

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service liveness status."""
    return HealthResponse(status="ok", version=__version__)


@router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    """Return service readiness status."""
    return HealthResponse(status="ok", version=__version__)
