"""Mapping between ResourceRelationship and HTTP schemas."""

from eke.domain.identity import ResourceUUID
from eke.domain.relationships import ResourceRelationship
from eke.domain.temporal import ValidityPeriod
from eke.presentation.api.schemas.resource_relationships import (
    ResourceRelationshipCreateRequest,
    ResourceRelationshipResponse,
)


def resource_relationship_from_request(
    source_uuid: ResourceUUID,
    request: ResourceRelationshipCreateRequest,
) -> ResourceRelationship:
    """Create a directed relationship from an HTTP request."""
    return ResourceRelationship(
        source=source_uuid,
        target=ResourceUUID.from_string(
            request.target_resource_uuid
        ),
        relationship_type=request.relationship_type,
        validity=ValidityPeriod(
            request.valid_from,
            request.valid_to,
        ),
    )


def resource_relationship_to_response(
    relationship: ResourceRelationship,
) -> ResourceRelationshipResponse:
    """Convert a relationship to an HTTP response."""
    return ResourceRelationshipResponse(
        source_resource_uuid=str(relationship.source),
        target_resource_uuid=str(relationship.target),
        relationship_type=relationship.relationship_type,
        valid_from=relationship.validity.valid_from,
        valid_to=relationship.validity.valid_to,
    )
