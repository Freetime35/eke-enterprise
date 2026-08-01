"""Resource status enumeration.

This module defines the canonical lifecycle status vocabulary used by
EKE Enterprise resources.
"""

from __future__ import annotations

from enum import StrEnum


class ResourceStatus(StrEnum):
    """Represent the canonical lifecycle status of a resource."""

    DRAFT = "DRAFT"
    ADOPTED = "ADOPTED"
    PUBLISHED = "PUBLISHED"
    IN_FORCE = "IN_FORCE"
    PARTIALLY_IN_FORCE = "PARTIALLY_IN_FORCE"
    NOT_YET_IN_FORCE = "NOT_YET_IN_FORCE"
    REPEALED = "REPEALED"
    EXPIRED = "EXPIRED"
    WITHDRAWN = "WITHDRAWN"
    ANNULLED = "ANNULLED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"

    @property
    def is_terminal(self) -> bool:
        """Return whether the status represents a terminal lifecycle state."""
        return self in {
            ResourceStatus.REPEALED,
            ResourceStatus.EXPIRED,
            ResourceStatus.WITHDRAWN,
            ResourceStatus.ANNULLED,
            ResourceStatus.SUPERSEDED,
        }

    @property
    def is_effective(self) -> bool:
        """Return whether the status indicates current legal effect."""
        return self in {
            ResourceStatus.IN_FORCE,
            ResourceStatus.PARTIALLY_IN_FORCE,
        }

    @property
    def is_pre_effective(self) -> bool:
        """Return whether the resource exists before legal effect."""
        return self in {
            ResourceStatus.DRAFT,
            ResourceStatus.ADOPTED,
            ResourceStatus.PUBLISHED,
            ResourceStatus.NOT_YET_IN_FORCE,
        }
