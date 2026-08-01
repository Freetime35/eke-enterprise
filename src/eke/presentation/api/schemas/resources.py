"""Pydantic schemas for Resource HTTP operations."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from eke.domain.identity import IdentifierScheme
from eke.domain.resources import ResourceStatus, ResourceType


class BusinessIdentifierSchema(BaseModel):
    """External business identifier representation."""

    model_config = ConfigDict(extra="forbid")

    scheme: IdentifierScheme
    value: str = Field(min_length=1)


class ResourceCreateRequest(BaseModel):
    """Create a Resource aggregate."""

    model_config = ConfigDict(extra="forbid")

    identifiers: list[BusinessIdentifierSchema] = Field(
        min_length=1
    )
    resource_type: ResourceType = ResourceType.OTHER
    status: ResourceStatus = ResourceStatus.UNKNOWN


class ResourceUpdateRequest(BaseModel):
    """Update the HTTP-editable fields of a Resource."""

    model_config = ConfigDict(extra="forbid")

    identifiers: list[BusinessIdentifierSchema] = Field(
        min_length=1
    )
    resource_type: ResourceType
    status: ResourceStatus


class ResourceResponse(BaseModel):
    """Resource representation returned by the API."""

    model_config = ConfigDict(extra="forbid")

    resource_uuid: str
    identifiers: list[BusinessIdentifierSchema]
    resource_type: ResourceType
    status: ResourceStatus
