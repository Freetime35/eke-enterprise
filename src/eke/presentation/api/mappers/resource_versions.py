"""Mapping between ResourceVersion and HTTP schemas."""

from eke.domain.identity import ResourceUUID, ResourceVersionUUID
from eke.domain.resources import ResourceVersion
from eke.domain.temporal import ValidityPeriod
from eke.presentation.api.schemas.resource_versions import (
    ResourceVersionCreateRequest,
    ResourceVersionResponse,
)


def resource_version_from_request(
    resource_uuid: ResourceUUID,
    request: ResourceVersionCreateRequest,
) -> ResourceVersion:
    """Create a ResourceVersion from an HTTP request."""
    previous_version_uuid = (
        ResourceVersionUUID.from_string(
            request.previous_version_uuid
        )
        if request.previous_version_uuid is not None
        else None
    )
    return ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=resource_uuid,
        status=request.status,
        validity=ValidityPeriod(
            request.valid_from,
            request.valid_to,
        ),
        previous_version_uuid=previous_version_uuid,
    )


def resource_version_to_response(
    version: ResourceVersion,
) -> ResourceVersionResponse:
    """Convert a ResourceVersion to an HTTP response."""
    return ResourceVersionResponse(
        version_uuid=str(version.version_uuid),
        resource_uuid=str(version.resource_uuid),
        status=version.status,
        valid_from=version.validity.valid_from,
        valid_to=version.validity.valid_to,
        previous_version_uuid=(
            str(version.previous_version_uuid)
            if version.previous_version_uuid is not None
            else None
        ),
    )
