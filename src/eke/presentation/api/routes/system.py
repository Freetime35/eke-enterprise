"""Operational HTTP endpoints."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text

from eke.presentation.api.container import ApplicationContainer
from eke.presentation.api.dependencies import get_container

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: Literal["ok"]


class ReadinessResponse(BaseModel):
    """Readiness endpoint response."""

    status: Literal["ready"]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Process health",
)
def health() -> HealthResponse:
    """Report whether the HTTP process is running."""
    return HealthResponse(status="ok")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Application readiness",
)
def ready(
    container: ApplicationContainer = Depends(
        get_container
    ),
) -> ReadinessResponse:
    """Report whether the database dependency is reachable."""
    with container.session_factory() as session:
        session.execute(text("SELECT 1"))
    return ReadinessResponse(status="ready")
