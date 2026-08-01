"""Resource version HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from eke.application.resources import ResourceVersionService
from eke.domain.identity import ResourceUUID, ResourceVersionUUID
from eke.presentation.api.dependencies import (
    get_resource_version_service,
)
from eke.presentation.api.mappers.resource_versions import (
    resource_version_from_request,
    resource_version_to_response,
)
from eke.presentation.api.schemas.resource_versions import (
    ResourceVersionCreateRequest,
    ResourceVersionResponse,
)

router = APIRouter(
    prefix="/resources/{resource_uuid}/versions",
    tags=["resource-versions"],
)

ResourceVersionServiceDependency = Annotated[
    ResourceVersionService,
    Depends(get_resource_version_service),
]


@router.get("", response_model=list[ResourceVersionResponse])
def list_resource_versions(
    resource_uuid: str,
    service: ResourceVersionServiceDependency,
) -> list[ResourceVersionResponse]:
    versions = service.list(_parse_resource_uuid(resource_uuid))
    return [
        resource_version_to_response(version)
        for version in versions
    ]


@router.post(
    "",
    response_model=ResourceVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_version(
    resource_uuid: str,
    request: ResourceVersionCreateRequest,
    service: ResourceVersionServiceDependency,
    response: Response,
) -> ResourceVersionResponse:
    parsed_resource_uuid = _parse_resource_uuid(resource_uuid)
    version = resource_version_from_request(
        parsed_resource_uuid,
        request,
    )
    created = service.add(parsed_resource_uuid, version)
    response.headers["Location"] = (
        f"/resources/{resource_uuid}/versions/"
        f"{created.version_uuid}"
    )
    return resource_version_to_response(created)


@router.get(
    "/{version_uuid}",
    response_model=ResourceVersionResponse,
)
def get_resource_version(
    resource_uuid: str,
    version_uuid: str,
    service: ResourceVersionServiceDependency,
) -> ResourceVersionResponse:
    version = service.get(
        _parse_resource_uuid(resource_uuid),
        _parse_version_uuid(version_uuid),
    )
    return resource_version_to_response(version)


@router.delete(
    "/{version_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource_version(
    resource_uuid: str,
    version_uuid: str,
    service: ResourceVersionServiceDependency,
) -> Response:
    service.remove(
        _parse_resource_uuid(resource_uuid),
        _parse_version_uuid(version_uuid),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _parse_resource_uuid(value: str) -> ResourceUUID:
    try:
        return ResourceUUID.from_string(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="resource_uuid must be a valid UUID",
        ) from exc


def _parse_version_uuid(value: str) -> ResourceVersionUUID:
    try:
        return ResourceVersionUUID.from_string(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="version_uuid must be a valid UUID",
        ) from exc
