"""Resource version internal identifier value object.

This module defines the immutable internal identifier assigned to every
canonical resource version managed by EKE Enterprise.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ResourceVersionUUID:
    """Represent the immutable internal identity of a resource version.

    Attributes:
        value: The wrapped UUID value.
    """

    value: UUID

    def __post_init__(self) -> None:
        """Validate the wrapped UUID value."""
        if not isinstance(self.value, UUID):
            raise TypeError("value must be an instance of uuid.UUID")

    @classmethod
    def generate(cls) -> ResourceVersionUUID:
        """Create a new randomly generated version identifier."""
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> ResourceVersionUUID:
        """Create a version identifier from canonical UUID text."""
        if not isinstance(value, str):
            raise TypeError("value must be a string")

        return cls(UUID(value))

    def __str__(self) -> str:
        """Return the canonical UUID string."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return an unambiguous developer representation."""
        return f"{self.__class__.__name__}('{self.value}')"
