"""Resource title HTTP endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from eke.application.resources import ResourceTitleService
from eke.domain.identity import ResourceUUID
from eke.domain.localization import LanguageCode
from eke.presentation.api.dependencies import get_resource_title_service
from eke.presentation.api.mappers.resource_titles import (
    resource_title_from_request,
    resource_title_to_response,
)
from eke.presentation.api.schemas.resource_titles import (
    ResourceTitleCreateRequest,
    ResourceTitleResponse,
)

router = APIRouter(
    prefix="/resources/{resource_uuid}/titles",
    tags=["resource-titles"],
)

ResourceTitleServiceDependency = Annotated[
    ResourceTitleService,
    Depends(get_resource_title_service),
]


@router.get("", response_model=list[ResourceTitleResponse])
def list_resource_titles(
    resource_uuid: str,
    service: ResourceTitleServiceDependency,
) -> list[ResourceTitleResponse]:
    return [
        resource_title_to_response(title)
        for title in service.list(_parse_resource_uuid(resource_uuid))
    ]


@router.post(
    "",
    response_model=ResourceTitleResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_title(
    resource_uuid: str,
    request: ResourceTitleCreateRequest,
    service: ResourceTitleServiceDependency,
) -> ResourceTitleResponse:
    title = resource_title_from_request(request)
    created = service.add(_parse_resource_uuid(resource_uuid), title)
    return resource_title_to_response(created)


@router.delete(
    "/{language}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource_title(
    resource_uuid: str,
    language: str,
    service: ResourceTitleServiceDependency,
    valid_from: Annotated[date | None, Query()] = None,
    valid_to: Annotated[date | None, Query()] = None,
) -> Response:
    service.remove(
        _parse_resource_uuid(resource_uuid),
        LanguageCode(language),
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
