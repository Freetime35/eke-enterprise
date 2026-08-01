"""Pydantic schemas for ProvenanceRecord operations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceSource,
)


class ProvenanceRecordCreateRequest(BaseModel):
    """Create immutable provenance for a Resource."""

    model_config = ConfigDict(extra="forbid")

    source: ProvenanceSource
    source_reference: str = Field(min_length=1)
    acquired_at: datetime
    acquisition_method: AcquisitionMethod
    checksum: str | None = Field(default=None, min_length=1)

    @field_validator("acquired_at")
    @classmethod
    def validate_acquired_at(
        cls,
        value: datetime,
    ) -> datetime:
        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                "acquired_at must be timezone-aware"
            )
        return value


class ProvenanceRecordResponse(BaseModel):
    """HTTP representation of a ProvenanceRecord."""

    model_config = ConfigDict(extra="forbid")

    resource_uuid: str
    source: ProvenanceSource
    source_reference: str
    acquired_at: datetime
    acquisition_method: AcquisitionMethod
    checksum: str | None
