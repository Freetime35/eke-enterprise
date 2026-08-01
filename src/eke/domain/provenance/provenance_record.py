"""Provenance record business concept.

This module defines immutable acquisition and traceability metadata for
canonical resource data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from eke.domain.identity import ResourceUUID
from eke.domain.provenance.acquisition_method import AcquisitionMethod
from eke.domain.provenance.provenance_source import ProvenanceSource


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """Represent immutable provenance for acquired resource data.

    Attributes:
        resource_uuid: Canonical resource associated with the record.
        source: Canonical source system or authority.
        source_reference: Stable source-side reference or locator.
        acquired_at: Time at which the data was acquired.
        acquisition_method: Method used to acquire the data.
        checksum: Optional content checksum supplied by ingestion.
    """

    resource_uuid: ResourceUUID
    source: ProvenanceSource
    source_reference: str
    acquired_at: datetime
    acquisition_method: AcquisitionMethod
    checksum: str | None = None

    def __post_init__(self) -> None:
        """Validate provenance invariants."""
        if not isinstance(self.resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        if not isinstance(self.source, ProvenanceSource):
            raise TypeError("source must be a ProvenanceSource")

        if not isinstance(self.source_reference, str):
            raise TypeError("source_reference must be a string")

        if not self.source_reference.strip():
            raise ValueError("source_reference must not be empty")

        if not isinstance(self.acquired_at, datetime):
            raise TypeError("acquired_at must be a datetime")

        if (
            self.acquired_at.tzinfo is None
            or self.acquired_at.utcoffset() is None
        ):
            raise ValueError("acquired_at must be timezone-aware")

        if not isinstance(
            self.acquisition_method,
            AcquisitionMethod,
        ):
            raise TypeError(
                "acquisition_method must be an AcquisitionMethod"
            )

        if self.checksum is not None:
            if not isinstance(self.checksum, str):
                raise TypeError("checksum must be a string or None")

            if not self.checksum.strip():
                raise ValueError("checksum must not be empty")

    @property
    def has_checksum(self) -> bool:
        """Return whether a checksum is available."""
        return self.checksum is not None

    def belongs_to(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether the record belongs to a resource."""
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        return self.resource_uuid == resource_uuid

    def comes_from(self, source: ProvenanceSource) -> bool:
        """Return whether the record comes from a source."""
        if not isinstance(source, ProvenanceSource):
            raise TypeError("source must be a ProvenanceSource")

        return self.source is source

    def was_acquired_by(
        self,
        acquisition_method: AcquisitionMethod,
    ) -> bool:
        """Return whether the record used an acquisition method."""
        if not isinstance(
            acquisition_method,
            AcquisitionMethod,
        ):
            raise TypeError(
                "acquisition_method must be an AcquisitionMethod"
            )

        return self.acquisition_method is acquisition_method
