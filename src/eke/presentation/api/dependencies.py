"""FastAPI dependency providers."""

from __future__ import annotations

from fastapi import Request

from eke.application.resources import ResourceService
from eke.presentation.api.container import ApplicationContainer


def get_container(request: Request) -> ApplicationContainer:
    """Return the process application container."""
    container = getattr(
        request.app.state,
        "container",
        None,
    )
    if not isinstance(container, ApplicationContainer):
        raise RuntimeError(
            "application container is not initialized"
        )
    return container


def get_resource_service(
    request: Request,
) -> ResourceService:
    """Create a ResourceService for the current request."""
    return get_container(request).resource_service()
