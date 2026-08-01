"""In-memory ResourceRepository implementation."""

from __future__ import annotations

from threading import RLock

from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.repositories import (
    ResourceRepository,
    ResourceSearchCriteria,
    ResourceSearchPage,
)
from eke.domain.resources import Resource


class InMemoryResourceRepository:
    """Store Resource aggregates in memory."""

    def __init__(self) -> None:
        self._resources: dict[ResourceUUID, Resource] = {}
        self._lock = RLock()

    def save(self, resource: Resource) -> None:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource")

        with self._lock:
            self._resources[resource.resource_uuid] = resource

    def get(
        self,
        resource_uuid: ResourceUUID,
    ) -> Resource | None:
        self._validate_resource_uuid(resource_uuid)

        with self._lock:
            return self._resources.get(resource_uuid)

    def get_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource | None:
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
        self._validate_resource_uuid(resource_uuid)

        with self._lock:
            return resource_uuid in self._resources

    def delete(self, resource_uuid: ResourceUUID) -> bool:
        self._validate_resource_uuid(resource_uuid)

        with self._lock:
            return (
                self._resources.pop(resource_uuid, None)
                is not None
            )

    def search(
        self,
        criteria: ResourceSearchCriteria,
    ) -> ResourceSearchPage:
        if not isinstance(criteria, ResourceSearchCriteria):
            raise TypeError(
                "criteria must be a ResourceSearchCriteria"
            )

        with self._lock:
            resources = tuple(self._resources.values())

        filtered = tuple(
            resource
            for resource in resources
            if _matches(resource, criteria)
        )
        ordered = tuple(
            sorted(
                filtered,
                key=lambda item: str(item.resource_uuid),
            )
        )
        page_items = ordered[
            criteria.offset:
            criteria.offset + criteria.limit
        ]

        return ResourceSearchPage(
            items=page_items,
            total=len(ordered),
            limit=criteria.limit,
            offset=criteria.offset,
        )

    def clear(self) -> None:
        with self._lock:
            self._resources.clear()

    def count(self) -> int:
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


def _matches(
    resource: Resource,
    criteria: ResourceSearchCriteria,
) -> bool:
    if (
        criteria.identifier_scheme is not None
        and not resource.has_identifier_scheme(
            criteria.identifier_scheme
        )
    ):
        return False

    if (
        criteria.resource_type is not None
        and resource.resource_type
        is not criteria.resource_type
    ):
        return False

    return not (
        criteria.status is not None
        and resource.status is not criteria.status
    )


resource_repository_contract: type[ResourceRepository]
resource_repository_contract = InMemoryResourceRepository
