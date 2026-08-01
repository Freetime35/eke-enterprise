"""Resource repository domain contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.repositories.resource_search import (
    ResourceSearchCriteria,
    ResourceSearchPage,
)
from eke.domain.resources import Resource


@runtime_checkable
class ResourceRepository(Protocol):
    """Define persistence operations for Resource aggregates."""

    def save(self, resource: Resource) -> None:
        """Create or replace a Resource aggregate."""

    def get(
        self,
        resource_uuid: ResourceUUID,
    ) -> Resource | None:
        """Return a Resource by internal identity, or None."""

    def get_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource | None:
        """Return a Resource by business identifier, or None."""

    def exists(
        self,
        resource_uuid: ResourceUUID,
    ) -> bool:
        """Return whether a Resource exists."""

    def delete(
        self,
        resource_uuid: ResourceUUID,
    ) -> bool:
        """Delete a Resource and report prior existence."""

    def search(
        self,
        criteria: ResourceSearchCriteria,
    ) -> ResourceSearchPage:
        """Return a stable filtered page of Resources."""
