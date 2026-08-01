"""Pydantic schemas for ResourceRelationship operations."""

from datetime import date

from pydantic import BaseModel, ConfigDict

from eke.domain.relationships import RelationshipType


class ResourceRelationshipCreateRequest(BaseModel):
    """Create an outgoing Resource relationship."""

    model_config = ConfigDict(extra="forbid")

    target_resource_uuid: str
    relationship_type: RelationshipType
    valid_from: date | None = None
    valid_to: date | None = None


class ResourceRelationshipResponse(BaseModel):
    """HTTP representation of a Resource relationship."""

    model_config = ConfigDict(extra="forbid")

    source_resource_uuid: str
    target_resource_uuid: str
    relationship_type: RelationshipType
    valid_from: date | None
    valid_to: date | None
