"""Resource CRUD and search HTTP endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from eke.application.resources import ResourceService
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.repositories import ResourceSearchCriteria
from eke.domain.resources import ResourceStatus, ResourceType
from eke.presentation.api.dependencies import (
    get_resource_service,
)
from eke.presentation.api.mappers import (
    resource_from_create,
    resource_from_update,
    resource_page_to_response,
    resource_to_response,
)
from eke.presentation.api.schemas import (
    ResourceCreateRequest,
    ResourceResponse,
    ResourceSearchResponse,
    ResourceUpdateRequest,
)

router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)

ResourceServiceDependency = Annotated[
    ResourceService,
    Depends(get_resource_service),
]


@router.post(
    "",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a resource",
)
def create_resource(
    request: ResourceCreateRequest,
    service: ResourceServiceDependency,
    response: Response,
) -> ResourceResponse:
    resource = resource_from_create(request)
    service.create(resource)
    response.headers["Location"] = (
        f"/resources/{resource.resource_uuid}"
    )
    return resource_to_response(resource)


@router.get(
    "",
    response_model=ResourceSearchResponse,
    summary="Search resources",
)
def search_resources(
    service: ResourceServiceDependency,
    identifier_scheme: Annotated[
        IdentifierScheme | None,
        Query(),
    ] = None,
    resource_type: Annotated[
        ResourceType | None,
        Query(),
    ] = None,
    resource_status: Annotated[
        ResourceStatus | None,
        Query(alias="status"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> ResourceSearchResponse:
    page = service.search(
        ResourceSearchCriteria(
            identifier_scheme=identifier_scheme,
            resource_type=resource_type,
            status=resource_status,
            limit=limit,
            offset=offset,
        )
    )
    return resource_page_to_response(page)


@router.get(
    "/by-identifier",
    response_model=ResourceResponse,
    summary="Get a resource by business identifier",
)
def get_resource_by_identifier(
    service: ResourceServiceDependency,
    scheme: Annotated[IdentifierScheme, Query()],
    value: Annotated[str, Query(min_length=1)],
) -> ResourceResponse:
    resource = service.find_by_identifier(
        BusinessIdentifier(scheme, value)
    )
    return resource_to_response(resource)


@router.get(
    "/{resource_uuid}",
    response_model=ResourceResponse,
    summary="Get a resource",
)
def get_resource(
    resource_uuid: str,
    service: ResourceServiceDependency,
) -> ResourceResponse:
    resource = service.get(
        _parse_resource_uuid(resource_uuid)
    )
    return resource_to_response(resource)


@router.put(
    "/{resource_uuid}",
    response_model=ResourceResponse,
    summary="Update a resource",
)
def update_resource(
    resource_uuid: str,
    request: ResourceUpdateRequest,
    service: ResourceServiceDependency,
) -> ResourceResponse:
    parsed_uuid = _parse_resource_uuid(resource_uuid)
    existing = service.get(parsed_uuid)
    updated = resource_from_update(existing, request)
    service.update(updated)
    return resource_to_response(updated)


@router.delete(
    "/{resource_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resource",
)
def delete_resource(
    resource_uuid: str,
    service: ResourceServiceDependency,
) -> Response:
    service.delete(_parse_resource_uuid(resource_uuid))
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


def _parse_resource_uuid(value: str) -> ResourceUUID:
    try:
        return ResourceUUID.from_string(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=(
                "resource_uuid must be a valid UUID"
            ),
        ) from exc
