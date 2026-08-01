"""Mapping between ProvenanceRecord and HTTP schemas."""

from eke.domain.identity import ResourceUUID
from eke.domain.provenance import ProvenanceRecord
from eke.presentation.api.schemas.resource_provenance import (
    ProvenanceRecordCreateRequest,
    ProvenanceRecordResponse,
)


def provenance_record_from_request(
    resource_uuid: ResourceUUID,
    request: ProvenanceRecordCreateRequest,
) -> ProvenanceRecord:
    """Create a ProvenanceRecord from an HTTP request."""
    return ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=request.source,
        source_reference=request.source_reference,
        acquired_at=request.acquired_at,
        acquisition_method=request.acquisition_method,
        checksum=request.checksum,
    )


def provenance_record_to_response(
    record: ProvenanceRecord,
) -> ProvenanceRecordResponse:
    """Convert a ProvenanceRecord to an HTTP response."""
    return ProvenanceRecordResponse(
        resource_uuid=str(record.resource_uuid),
        source=record.source,
        source_reference=record.source_reference,
        acquired_at=record.acquired_at,
        acquisition_method=record.acquisition_method,
        checksum=record.checksum,
    )
