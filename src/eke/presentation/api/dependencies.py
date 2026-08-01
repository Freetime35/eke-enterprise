"""FastAPI dependency providers."""

from fastapi import Request

from eke.application.eurlex import (
    EurLexBulkImportService,
    EurLexImportJobService,
    EurLexResourceImportService,
)
from eke.application.resources import (
    ResourceClassificationService,
    ResourceProvenanceService,
    ResourceRelationshipService,
    ResourceService,
    ResourceTitleService,
    ResourceVersionService,
)
from eke.presentation.api.container import ApplicationContainer


def get_container(request: Request) -> ApplicationContainer:
    """Return the initialized application container."""
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
    return get_container(request).resource_service()


def get_resource_title_service(
    request: Request,
) -> ResourceTitleService:
    return get_container(request).resource_title_service()


def get_resource_version_service(
    request: Request,
) -> ResourceVersionService:
    return get_container(request).resource_version_service()


def get_resource_relationship_service(
    request: Request,
) -> ResourceRelationshipService:
    return get_container(
        request
    ).resource_relationship_service()


def get_resource_provenance_service(
    request: Request,
) -> ResourceProvenanceService:
    return get_container(
        request
    ).resource_provenance_service()


def get_resource_classification_service(
    request: Request,
) -> ResourceClassificationService:
    return get_container(
        request
    ).resource_classification_service()


def get_eurlex_import_service(
    request: Request,
) -> EurLexResourceImportService:
    return get_container(request).eurlex_import_service()


def get_eurlex_bulk_import_service(
    request: Request,
) -> EurLexBulkImportService:
    return get_container(
        request
    ).eurlex_bulk_import_service()


def get_import_job_service(
    request: Request,
) -> EurLexImportJobService:
    return get_container(request).import_job_service()
