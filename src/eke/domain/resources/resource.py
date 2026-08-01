"""Resource aggregate root.

This module defines the canonical Resource aggregate root used by
EKE Enterprise.
"""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)


@dataclass(frozen=True, slots=True)
class Resource:
    """Represent a canonical resource managed by EKE Enterprise.

    A Resource owns one immutable internal identifier and one or more
    external business identifiers.

    Attributes:
        resource_uuid: Immutable internal resource identity.
        identifiers: External business identifiers assigned to the resource.
    """

    resource_uuid: ResourceUUID
    identifiers: tuple[BusinessIdentifier, ...]

    def __post_init__(self) -> None:
        """Validate aggregate invariants."""
        if not isinstance(self.resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        if not isinstance(self.identifiers, tuple):
            raise TypeError("identifiers must be a tuple")

        if not self.identifiers:
            raise ValueError("a resource must have at least one business identifier")

        if not all(
            isinstance(identifier, BusinessIdentifier)
            for identifier in self.identifiers
        ):
            raise TypeError(
                "identifiers must contain only BusinessIdentifier instances"
            )

        if len(set(self.identifiers)) != len(self.identifiers):
            raise ValueError("business identifiers must be unique")

        schemes = tuple(identifier.scheme for identifier in self.identifiers)
        if len(set(schemes)) != len(schemes):
            raise ValueError(
                "a resource must not contain multiple identifiers "
                "for the same scheme"
            )

    def has_identifier(self, identifier: BusinessIdentifier) -> bool:
        """Return whether the resource owns the given identifier.

        Args:
            identifier: Business identifier to locate.

        Returns:
            True when the identifier belongs to the resource.

        Raises:
            TypeError: If identifier is not a BusinessIdentifier.
        """
        if not isinstance(identifier, BusinessIdentifier):
            raise TypeError("identifier must be a BusinessIdentifier")

        return identifier in self.identifiers

    def find_identifier(
        self,
        scheme: IdentifierScheme,
    ) -> BusinessIdentifier | None:
        """Find the business identifier assigned under a scheme.

        Args:
            scheme: Identifier scheme to search for.

        Returns:
            The matching business identifier, or None when no identifier
            exists for the requested scheme.

        Raises:
            TypeError: If scheme is not an IdentifierScheme.
        """
        if not isinstance(scheme, IdentifierScheme):
            raise TypeError("scheme must be an IdentifierScheme")

        return next(
            (
                identifier
                for identifier in self.identifiers
                if identifier.scheme is scheme
            ),
            None,
        )

    def has_identifier_scheme(self, scheme: IdentifierScheme) -> bool:
        """Return whether the resource has an identifier for a scheme.

        Args:
            scheme: Identifier scheme to locate.

        Returns:
            True when an identifier exists for the requested scheme.

        Raises:
            TypeError: If scheme is not an IdentifierScheme.
        """
        return self.find_identifier(scheme) is not None
