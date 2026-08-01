"""Resource repository domain contract.

This module defines the persistence abstraction used to load and store
Resource aggregates without coupling the domain to a database,
framework, or transport.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.resources import Resource


@runtime_checkable
class ResourceRepository(Protocol):
    """Define the persistence contract for Resource aggregates.

    Implementations may use relational databases, graph databases,
    document stores, in-memory collections, or remote services.
    """

    def save(self, resource: Resource) -> None:
        """Create or replace a Resource aggregate."""

    def get(self, resource_uuid: ResourceUUID) -> Resource | None:
        """Return a Resource by internal identity, or None."""

    def get_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource | None:
        """Return a Resource by external business identifier, or None."""

    def exists(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether a Resource exists for the identity."""

    def delete(self, resource_uuid: ResourceUUID) -> bool:
        """Delete a Resource and return whether it previously existed."""
