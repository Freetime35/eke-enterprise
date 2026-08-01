"""Resource relationship HTTP endpoints."""

from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from eke.application.resources import (
    ResourceRelationshipService,
)
from eke.domain.identity import ResourceUUID
from eke.domain.relationships import RelationshipType
from eke.presentation.api.dependencies import (
    get_resource_relationship_service,
)
from eke.presentation.api.mappers.resource_relationships import (
    resource_relationship_from_request,
    resource_relationship_to_response,
)
from eke.presentation.api.schemas.resource_relationships import (
    ResourceRelationshipCreateRequest,
    ResourceRelationshipResponse,
)

router = APIRouter(
    prefix="/resources/{resource_uuid}/relationships",
    tags=["resource-relationships"],
)

ResourceRelationshipServiceDependency = Annotated[
    ResourceRelationshipService,
    Depends(get_resource_relationship_service),
]


@router.get(
    "",
    response_model=list[ResourceRelationshipResponse],
)
def list_resource_relationships(
    resource_uuid: str,
    service: ResourceRelationshipServiceDependency,
) -> list[ResourceRelationshipResponse]:
    relationships = service.list(
        _parse_resource_uuid(resource_uuid)
    )
    return [
        resource_relationship_to_response(relationship)
        for relationship in relationships
    ]


@router.post(
    "",
    response_model=ResourceRelationshipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_relationship(
    resource_uuid: str,
    request: ResourceRelationshipCreateRequest,
    service: ResourceRelationshipServiceDependency,
) -> ResourceRelationshipResponse:
    source_uuid = _parse_resource_uuid(resource_uuid)
    try:
        relationship = resource_relationship_from_request(
            source_uuid,
            request,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="target_resource_uuid must be a valid UUID",
        ) from exc

    created = service.add(source_uuid, relationship)
    return resource_relationship_to_response(created)


@router.delete(
    "/{target_resource_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource_relationship(
    resource_uuid: str,
    target_resource_uuid: str,
    service: ResourceRelationshipServiceDependency,
    relationship_type: Annotated[
        RelationshipType,
        Query(),
    ],
    valid_from: Annotated[
        date | None,
        Query(),
    ] = None,
    valid_to: Annotated[
        date | None,
        Query(),
    ] = None,
) -> Response:
    service.remove(
        _parse_resource_uuid(resource_uuid),
        _parse_resource_uuid(target_resource_uuid),
        relationship_type,
        valid_from,
        valid_to,
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
