"""Resource internal identifier value object.

This module defines the immutable internal identifier assigned to every
resource managed by EKE Enterprise.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class ResourceUUID:
    """Represent the immutable internal identity of a resource.

    A ResourceUUID is independent of external business identifiers such as
    CELEX, ELI, CELLAR, ECLI, or source-specific document identifiers.

    Attributes:
        value: The wrapped UUID value.
    """

    value: UUID

    def __post_init__(self) -> None:
        """Validate the wrapped UUID value."""
        if not isinstance(self.value, UUID):
            raise TypeError("value must be an instance of uuid.UUID")

    @classmethod
    def generate(cls) -> ResourceUUID:
        """Create a new randomly generated resource identifier.

        Returns:
            A new ResourceUUID backed by a UUID version 4 value.
        """
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> ResourceUUID:
        """Create a resource identifier from its canonical string form.

        Args:
            value: Canonical UUID text.

        Returns:
            A ResourceUUID containing the parsed UUID.

        Raises:
            TypeError: If value is not a string.
            ValueError: If value is not a valid UUID representation.
        """
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        return cls(UUID(value))

    def __str__(self) -> str:
        """Return the canonical UUID string."""
        return str(self.value)

    def __repr__(self) -> str:
        """Return an unambiguous developer representation."""
        return f"{self.__class__.__name__}('{self.value}')"
