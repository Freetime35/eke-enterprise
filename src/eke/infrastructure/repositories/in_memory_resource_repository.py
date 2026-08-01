"""In-memory ResourceRepository implementation.

This module provides a deterministic in-memory repository suitable for
tests, local development, and application-service prototyping.
"""

from __future__ import annotations

from threading import RLock

from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.repositories import ResourceRepository
from eke.domain.resources import Resource


class InMemoryResourceRepository:
    """Store Resource aggregates in memory.

    The implementation is thread-safe for individual repository
    operations and structurally conforms to ResourceRepository.
    """

    def __init__(self) -> None:
        self._resources: dict[ResourceUUID, Resource] = {}
        self._lock = RLock()

    def save(self, resource: Resource) -> None:
        """Create or replace a Resource aggregate."""
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource")

        with self._lock:
            self._resources[resource.resource_uuid] = resource

    def get(self, resource_uuid: ResourceUUID) -> Resource | None:
        """Return a Resource by internal identity, or None."""
        self._validate_resource_uuid(resource_uuid)

        with self._lock:
            return self._resources.get(resource_uuid)

    def get_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource | None:
        """Return a Resource by external business identifier, or None."""
        if not isinstance(identifier, BusinessIdentifier):
            raise TypeError(
                "identifier must be a BusinessIdentifier"
            )

        with self._lock:
            return next(
                (
                    resource
                    for resource in self._resources.values()
                    if resource.has_identifier(identifier)
                ),
                None,
            )

    def exists(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether a Resource exists for the identity."""
        self._validate_resource_uuid(resource_uuid)

        with self._lock:
            return resource_uuid in self._resources

    def delete(self, resource_uuid: ResourceUUID) -> bool:
        """Delete a Resource and return whether it previously existed."""
        self._validate_resource_uuid(resource_uuid)

        with self._lock:
            return (
                self._resources.pop(resource_uuid, None)
                is not None
            )

    def clear(self) -> None:
        """Remove all resources from the repository."""
        with self._lock:
            self._resources.clear()

    def count(self) -> int:
        """Return the number of stored resources."""
        with self._lock:
            return len(self._resources)

    @staticmethod
    def _validate_resource_uuid(
        resource_uuid: ResourceUUID,
    ) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError(
                "resource_uuid must be a ResourceUUID"
            )


resource_repository_contract: type[ResourceRepository]
resource_repository_contract = InMemoryResourceRepository
