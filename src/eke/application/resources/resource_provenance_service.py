"""Application service for Resource provenance use cases."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from eke.application.resources.exceptions import (
    ProvenanceRecordAlreadyExistsError,
    ProvenanceRecordConflictError,
    ProvenanceRecordNotFoundError,
    ResourceNotFoundError,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import ResourceUUID
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceRecord,
    ProvenanceSource,
)
from eke.domain.resources import Resource


class ResourceProvenanceService:
    """Coordinate provenance operations on Resource aggregates."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
    ) -> None:
        if not callable(unit_of_work_factory):
            raise TypeError("unit_of_work_factory must be callable")
        self._unit_of_work_factory = unit_of_work_factory

    def list(
        self,
        resource_uuid: ResourceUUID,
    ) -> tuple[ProvenanceRecord, ...]:
        """Return all provenance records of a Resource."""
        self._validate_resource_uuid(resource_uuid)

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )
            return resource.provenance_records

    def add(
        self,
        resource_uuid: ResourceUUID,
        record: ProvenanceRecord,
    ) -> ProvenanceRecord:
        """Add immutable provenance to a Resource."""
        self._validate_resource_uuid(resource_uuid)
        if not isinstance(record, ProvenanceRecord):
            raise TypeError(
                "record must be a ProvenanceRecord"
            )
        if not record.belongs_to(resource_uuid):
            raise ProvenanceRecordConflictError(
                "provenance record belongs to another resource"
            )

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )

            if record in resource.provenance_records:
                raise ProvenanceRecordAlreadyExistsError(
                    "provenance record already exists"
                )

            updated = _replace_provenance(
                resource,
                (*resource.provenance_records, record),
            )
            uow.resources.save(updated)
            uow.commit()
            return record

    def remove(
        self,
        resource_uuid: ResourceUUID,
        source: ProvenanceSource,
        source_reference: str,
        acquired_at: datetime,
        acquisition_method: AcquisitionMethod,
        checksum: str | None,
    ) -> None:
        """Remove one precisely identified provenance record."""
        self._validate_resource_uuid(resource_uuid)

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )

            remaining = tuple(
                record
                for record in resource.provenance_records
                if not _matches(
                    record,
                    source,
                    source_reference,
                    acquired_at,
                    acquisition_method,
                    checksum,
                )
            )
            if len(remaining) == len(
                resource.provenance_records
            ):
                raise ProvenanceRecordNotFoundError(
                    "provenance record not found"
                )

            uow.resources.save(
                _replace_provenance(resource, remaining)
            )
            uow.commit()

    @staticmethod
    def _validate_resource_uuid(
        resource_uuid: ResourceUUID,
    ) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError(
                "resource_uuid must be a ResourceUUID"
            )


def _matches(
    record: ProvenanceRecord,
    source: ProvenanceSource,
    source_reference: str,
    acquired_at: datetime,
    acquisition_method: AcquisitionMethod,
    checksum: str | None,
) -> bool:
    return (
        record.source is source
        and record.source_reference == source_reference
        and record.acquired_at == acquired_at
        and record.acquisition_method is acquisition_method
        and record.checksum == checksum
    )


def _replace_provenance(
    resource: Resource,
    provenance_records: tuple[ProvenanceRecord, ...],
) -> Resource:
    return Resource(
        resource_uuid=resource.resource_uuid,
        identifiers=resource.identifiers,
        resource_type=resource.resource_type,
        status=resource.status,
        titles=resource.titles,
        versions=resource.versions,
        relationships=resource.relationships,
        provenance_records=provenance_records,
        classifications=resource.classifications,
    )
