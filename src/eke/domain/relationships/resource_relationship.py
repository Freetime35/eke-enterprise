"""Resource relationship business concept.

This module defines a directed relationship between two canonical
resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.domain.identity import ResourceUUID
from eke.domain.relationships.relationship_type import RelationshipType
from eke.domain.temporal import ValidityPeriod


@dataclass(frozen=True, slots=True)
class ResourceRelationship:
    """Represent a directed relationship between two resources.

    Attributes:
        source: Resource from which the relationship originates.
        target: Resource to which the relationship points.
        relationship_type: Canonical relationship classification.
        validity: Inclusive temporal validity of the relationship.
    """

    source: ResourceUUID
    target: ResourceUUID
    relationship_type: RelationshipType
    validity: ValidityPeriod = ValidityPeriod()

    def __post_init__(self) -> None:
        """Validate relationship invariants."""
        if not isinstance(self.source, ResourceUUID):
            raise TypeError("source must be a ResourceUUID")

        if not isinstance(self.target, ResourceUUID):
            raise TypeError("target must be a ResourceUUID")

        if self.source == self.target:
            raise ValueError("source and target must identify different resources")

        if not isinstance(self.relationship_type, RelationshipType):
            raise TypeError(
                "relationship_type must be a RelationshipType"
            )

        if not isinstance(self.validity, ValidityPeriod):
            raise TypeError("validity must be a ValidityPeriod")

    def connects(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether the relationship touches a resource.

        Args:
            resource_uuid: Resource identity to locate.

        Returns:
            True when the resource is the source or target.

        Raises:
            TypeError: If resource_uuid is not a ResourceUUID.
        """
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        return resource_uuid in (self.source, self.target)

    def originates_from(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether a resource is the relationship source."""
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        return self.source == resource_uuid

    def points_to(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether a resource is the relationship target."""
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        return self.target == resource_uuid

    def is_active_on(self, value: date) -> bool:
        """Return whether the relationship is valid on a date."""
        return self.validity.contains(value)
