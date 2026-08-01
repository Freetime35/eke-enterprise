"""Resource version business concept.

This module defines a canonical immutable version of a resource.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.domain.identity import ResourceUUID, ResourceVersionUUID
from eke.domain.resources.resource_status import ResourceStatus
from eke.domain.temporal import ValidityPeriod


@dataclass(frozen=True, slots=True)
class ResourceVersion:
    """Represent one canonical version of a resource.

    Attributes:
        version_uuid: Immutable identity of this version.
        resource_uuid: Identity of the owning resource.
        status: Lifecycle status of this version.
        validity: Inclusive temporal validity of this version.
        previous_version_uuid: Optional identity of the preceding version.
    """

    version_uuid: ResourceVersionUUID
    resource_uuid: ResourceUUID
    status: ResourceStatus
    validity: ValidityPeriod = ValidityPeriod()
    previous_version_uuid: ResourceVersionUUID | None = None

    def __post_init__(self) -> None:
        """Validate version invariants."""
        if not isinstance(self.version_uuid, ResourceVersionUUID):
            raise TypeError(
                "version_uuid must be a ResourceVersionUUID"
            )

        if not isinstance(self.resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        if not isinstance(self.status, ResourceStatus):
            raise TypeError("status must be a ResourceStatus")

        if not isinstance(self.validity, ValidityPeriod):
            raise TypeError("validity must be a ValidityPeriod")

        if (
            self.previous_version_uuid is not None
            and not isinstance(
                self.previous_version_uuid,
                ResourceVersionUUID,
            )
        ):
            raise TypeError(
                "previous_version_uuid must be a "
                "ResourceVersionUUID or None"
            )

        if self.previous_version_uuid == self.version_uuid:
            raise ValueError(
                "a resource version cannot reference itself "
                "as its previous version"
            )

    @property
    def is_effective(self) -> bool:
        """Return whether the version has current legal effect."""
        return self.status.is_effective

    @property
    def is_terminal(self) -> bool:
        """Return whether the version has a terminal lifecycle status."""
        return self.status.is_terminal

    @property
    def has_previous_version(self) -> bool:
        """Return whether the version references a preceding version."""
        return self.previous_version_uuid is not None

    def belongs_to(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether the version belongs to a resource."""
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        return self.resource_uuid == resource_uuid

    def is_valid_on(self, value: date) -> bool:
        """Return whether the version is valid on a date."""
        return self.validity.contains(value)

    def succeeds(self, other: ResourceVersion) -> bool:
        """Return whether this version directly succeeds another version.

        A version directly succeeds another version when both belong to
        the same resource and this version references the other version
        as its previous version.
        """
        if not isinstance(other, ResourceVersion):
            raise TypeError("other must be a ResourceVersion")

        return (
            self.resource_uuid == other.resource_uuid
            and self.previous_version_uuid == other.version_uuid
        )
