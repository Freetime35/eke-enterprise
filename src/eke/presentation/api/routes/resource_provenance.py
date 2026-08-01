"""Resource provenance HTTP endpoints."""

from datetime import datetime
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
    ResourceProvenanceService,
)
from eke.domain.identity import ResourceUUID
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceSource,
)
from eke.presentation.api.dependencies import (
    get_resource_provenance_service,
)
from eke.presentation.api.mappers.resource_provenance import (
    provenance_record_from_request,
    provenance_record_to_response,
)
from eke.presentation.api.schemas.resource_provenance import (
    ProvenanceRecordCreateRequest,
    ProvenanceRecordResponse,
)

router = APIRouter(
    prefix="/resources/{resource_uuid}/provenance",
    tags=["resource-provenance"],
)

ResourceProvenanceServiceDependency = Annotated[
    ResourceProvenanceService,
    Depends(get_resource_provenance_service),
]


@router.get(
    "",
    response_model=list[ProvenanceRecordResponse],
)
def list_resource_provenance(
    resource_uuid: str,
    service: ResourceProvenanceServiceDependency,
) -> list[ProvenanceRecordResponse]:
    records = service.list(
        _parse_resource_uuid(resource_uuid)
    )
    return [
        provenance_record_to_response(record)
        for record in records
    ]


@router.post(
    "",
    response_model=ProvenanceRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_resource_provenance(
    resource_uuid: str,
    request: ProvenanceRecordCreateRequest,
    service: ResourceProvenanceServiceDependency,
) -> ProvenanceRecordResponse:
    parsed_uuid = _parse_resource_uuid(resource_uuid)
    record = provenance_record_from_request(
        parsed_uuid,
        request,
    )
    created = service.add(parsed_uuid, record)
    return provenance_record_to_response(created)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource_provenance(
    resource_uuid: str,
    service: ResourceProvenanceServiceDependency,
    source: Annotated[ProvenanceSource, Query()],
    source_reference: Annotated[str, Query(min_length=1)],
    acquired_at: Annotated[datetime, Query()],
    acquisition_method: Annotated[
        AcquisitionMethod,
        Query(),
    ],
    checksum: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
) -> Response:
    if (
        acquired_at.tzinfo is None
        or acquired_at.utcoffset() is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="acquired_at must be timezone-aware",
        )

    service.remove(
        _parse_resource_uuid(resource_uuid),
        source,
        source_reference,
        acquired_at,
        acquisition_method,
        checksum,
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
