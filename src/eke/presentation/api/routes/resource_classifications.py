"""Resource classification HTTP endpoints."""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from eke.application.resources import (
    ResourceClassificationService,
)
from eke.domain.classification import ClassificationScheme
from eke.domain.identity import ResourceUUID
from eke.domain.localization import LanguageCode
from eke.presentation.api.dependencies import (
    get_resource_classification_service,
)
from eke.presentation.api.mappers.resource_classifications import (
    resource_classification_from_request,
    resource_classification_to_response,
)
from eke.presentation.api.schemas.resource_classifications import (
    ResourceClassificationCreateRequest,
    ResourceClassificationResponse,
)

router = APIRouter(
    prefix="/resources/{resource_uuid}/classifications",
    tags=["resource-classifications"],
)

ResourceClassificationServiceDependency = Annotated[
    ResourceClassificationService,
    Depends(get_resource_classification_service),
]


@router.get(
    "",
    response_model=list[ResourceClassificationResponse],
)
def list_resource_classifications(
    resource_uuid: str,
    service: ResourceClassificationServiceDependency,
) -> list[ResourceClassificationResponse]:
    classifications = service.list(
        _parse_resource_uuid(resource_uuid)
    )
    return [
        resource_classification_to_response(classification)
        for classification in classifications
    ]


@router.post(
    "",
    response_model=ResourceClassificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_classification(
    resource_uuid: str,
    request: ResourceClassificationCreateRequest,
    service: ResourceClassificationServiceDependency,
) -> ResourceClassificationResponse:
    classification = resource_classification_from_request(
        request
    )
    created = service.add(
        _parse_resource_uuid(resource_uuid),
        classification,
    )
    return resource_classification_to_response(created)


@router.delete(
    "/{scheme}/{code}/{language}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource_classification(
    resource_uuid: str,
    scheme: ClassificationScheme,
    code: str,
    language: str,
    service: ResourceClassificationServiceDependency,
) -> Response:
    service.remove(
        _parse_resource_uuid(resource_uuid),
        scheme,
        code,
        LanguageCode(language),
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
