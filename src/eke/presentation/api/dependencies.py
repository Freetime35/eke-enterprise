"""FastAPI dependency providers."""

from fastapi import Request

from eke.application.resources import (
    ResourceService,
    ResourceTitleService,
    ResourceVersionService,
)
from eke.presentation.api.container import ApplicationContainer


def get_container(request: Request) -> ApplicationContainer:
    container = getattr(request.app.state, "container", None)
    if not isinstance(container, ApplicationContainer):
        raise RuntimeError("application container is not initialized")
    return container


def get_resource_service(request: Request) -> ResourceService:
    return get_container(request).resource_service()


def get_resource_title_service(
    request: Request,
) -> ResourceTitleService:
    return get_container(request).resource_title_service()


def get_resource_version_service(
    request: Request,
) -> ResourceVersionService:
    return get_container(request).resource_version_service()
