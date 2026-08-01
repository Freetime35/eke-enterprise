"""Pydantic schemas for ResourceVersion operations."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from eke.domain.resources import ResourceStatus


class ResourceVersionCreateRequest(BaseModel):
    """Create a ResourceVersion."""

    model_config = ConfigDict(extra="forbid")

    status: ResourceStatus
    valid_from: date | None = None
    valid_to: date | None = None
    previous_version_uuid: str | None = None


class ResourceVersionResponse(BaseModel):
    """HTTP representation of a ResourceVersion."""

    model_config = ConfigDict(extra="forbid")

    version_uuid: str
    resource_uuid: str
    status: ResourceStatus
    valid_from: date | None
    valid_to: date | None
    previous_version_uuid: str | None
