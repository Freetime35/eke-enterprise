"""Mapping between Resource domain objects and HTTP schemas."""

from __future__ import annotations

from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.resources import Resource
from eke.presentation.api.schemas import (
    BusinessIdentifierSchema,
    ResourceCreateRequest,
    ResourceResponse,
    ResourceUpdateRequest,
)


def resource_from_create(
    request: ResourceCreateRequest,
) -> Resource:
    """Create a new Resource aggregate from an HTTP request."""
    if not isinstance(request, ResourceCreateRequest):
        raise TypeError(
            "request must be a ResourceCreateRequest"
        )

    return Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=_identifiers_from_schemas(
            request.identifiers
        ),
        resource_type=request.resource_type,
        status=request.status,
    )


def resource_from_update(
    existing: Resource,
    request: ResourceUpdateRequest,
) -> Resource:
    """Apply editable HTTP fields while preserving rich state."""
    if not isinstance(existing, Resource):
        raise TypeError("existing must be a Resource")
    if not isinstance(request, ResourceUpdateRequest):
        raise TypeError(
            "request must be a ResourceUpdateRequest"
        )

    return Resource(
        resource_uuid=existing.resource_uuid,
        identifiers=_identifiers_from_schemas(
            request.identifiers
        ),
        resource_type=request.resource_type,
        status=request.status,
        titles=existing.titles,
        versions=existing.versions,
        relationships=existing.relationships,
        provenance_records=existing.provenance_records,
        classifications=existing.classifications,
    )


def resource_to_response(
    resource: Resource,
) -> ResourceResponse:
    """Convert a Resource aggregate to its HTTP representation."""
    if not isinstance(resource, Resource):
        raise TypeError("resource must be a Resource")

    return ResourceResponse(
        resource_uuid=str(resource.resource_uuid),
        identifiers=[
            BusinessIdentifierSchema(
                scheme=identifier.scheme,
                value=identifier.value,
            )
            for identifier in resource.identifiers
        ],
        resource_type=resource.resource_type,
        status=resource.status,
    )


def _identifiers_from_schemas(
    identifiers: list[BusinessIdentifierSchema],
) -> tuple[BusinessIdentifier, ...]:
    return tuple(
        BusinessIdentifier(
            identifier.scheme,
            identifier.value,
        )
        for identifier in identifiers
    )
