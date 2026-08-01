from datetime import UTC, datetime

import pytest

from eke.application.resources import (
    ProvenanceRecordAlreadyExistsError,
    ProvenanceRecordNotFoundError,
    ResourceProvenanceService,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceRecord,
    ProvenanceSource,
)
from eke.domain.resources import Resource
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork

ACQUIRED_AT = datetime(
    2026,
    8,
    1,
    12,
    0,
    tzinfo=UTC,
)


def make_service() -> tuple[
    ResourceProvenanceService,
    Resource,
]:
    repository = InMemoryResourceRepository()
    resource = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )
    repository.save(resource)
    return (
        ResourceProvenanceService(
            lambda: InMemoryUnitOfWork(repository)
        ),
        resource,
    )


def make_record(
    resource_uuid: ResourceUUID,
) -> ProvenanceRecord:
    return ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="32023R1114",
        acquired_at=ACQUIRED_AT,
        acquisition_method=AcquisitionMethod.API,
        checksum="sha256:abc",
    )


def test_add_and_list_provenance() -> None:
    service, resource = make_service()
    record = make_record(resource.resource_uuid)

    service.add(resource.resource_uuid, record)

    assert service.list(resource.resource_uuid) == (
        record,
    )


def test_duplicate_provenance_is_rejected() -> None:
    service, resource = make_service()
    record = make_record(resource.resource_uuid)
    service.add(resource.resource_uuid, record)

    with pytest.raises(
        ProvenanceRecordAlreadyExistsError
    ):
        service.add(resource.resource_uuid, record)


def test_remove_provenance() -> None:
    service, resource = make_service()
    record = make_record(resource.resource_uuid)
    service.add(resource.resource_uuid, record)

    service.remove(
        resource.resource_uuid,
        record.source,
        record.source_reference,
        record.acquired_at,
        record.acquisition_method,
        record.checksum,
    )

    assert service.list(resource.resource_uuid) == ()


def test_remove_missing_provenance_is_rejected() -> None:
    service, resource = make_service()
    record = make_record(resource.resource_uuid)

    with pytest.raises(ProvenanceRecordNotFoundError):
        service.remove(
            resource.resource_uuid,
            record.source,
            record.source_reference,
            record.acquired_at,
            record.acquisition_method,
            record.checksum,
        )
