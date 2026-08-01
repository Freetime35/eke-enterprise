"""Tests for the ResourceRepository protocol."""

from __future__ import annotations

from dataclasses import dataclass, field

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.repositories import (
    ResourceRepository,
    ResourceSearchCriteria,
    ResourceSearchPage,
)
from eke.domain.resources import Resource


def make_identifier(
    value: str = "32023R1114",
) -> BusinessIdentifier:
    return BusinessIdentifier(
        scheme=IdentifierScheme.CELEX,
        value=value,
    )


def make_resource(
    resource_uuid: ResourceUUID | None = None,
    identifier: BusinessIdentifier | None = None,
) -> Resource:
    return Resource(
        resource_uuid=resource_uuid or ResourceUUID.generate(),
        identifiers=(identifier or make_identifier(),),
    )


@dataclass
class InMemoryResourceRepository:
    resources: dict[ResourceUUID, Resource] = field(
        default_factory=dict
    )

    def save(self, resource: Resource) -> None:
        self.resources[resource.resource_uuid] = resource

    def get(
        self,
        resource_uuid: ResourceUUID,
    ) -> Resource | None:
        return self.resources.get(resource_uuid)

    def get_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource | None:
        return next(
            (
                resource
                for resource in self.resources.values()
                if resource.has_identifier(identifier)
            ),
            None,
        )

    def exists(self, resource_uuid: ResourceUUID) -> bool:
        return resource_uuid in self.resources

    def delete(self, resource_uuid: ResourceUUID) -> bool:
        return self.resources.pop(resource_uuid, None) is not None

    def search(
        self,
        criteria: ResourceSearchCriteria,
    ) -> ResourceSearchPage:
        if not isinstance(criteria, ResourceSearchCriteria):
            raise TypeError(
                "criteria must be a ResourceSearchCriteria"
            )

        ordered = tuple(
            sorted(
                self.resources.values(),
                key=lambda resource: str(resource.resource_uuid),
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


def test_structural_implementation_satisfies_protocol() -> None:
    repository = InMemoryResourceRepository()

    assert isinstance(repository, ResourceRepository)


def test_save_and_get_resource() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()
    resource = make_resource()

    repository.save(resource)

    assert repository.get(resource.resource_uuid) == resource


def test_save_replaces_existing_resource() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()
    resource_uuid = ResourceUUID.generate()
    first = make_resource(
        resource_uuid=resource_uuid,
        identifier=make_identifier("32023R1114"),
    )
    replacement = make_resource(
        resource_uuid=resource_uuid,
        identifier=make_identifier("32013R0575"),
    )

    repository.save(first)
    repository.save(replacement)

    assert repository.get(resource_uuid) == replacement


def test_get_returns_none_for_missing_resource() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()

    assert repository.get(ResourceUUID.generate()) is None


def test_get_by_identifier_returns_matching_resource() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()
    identifier = make_identifier()
    resource = make_resource(identifier=identifier)

    repository.save(resource)

    assert repository.get_by_identifier(identifier) == resource


def test_get_by_identifier_returns_none_when_missing() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()

    assert repository.get_by_identifier(make_identifier()) is None


def test_exists_reports_presence() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()
    resource = make_resource()

    assert not repository.exists(resource.resource_uuid)

    repository.save(resource)

    assert repository.exists(resource.resource_uuid)


def test_delete_returns_true_for_existing_resource() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()
    resource = make_resource()
    repository.save(resource)

    assert repository.delete(resource.resource_uuid)
    assert not repository.exists(resource.resource_uuid)


def test_delete_returns_false_for_missing_resource() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()

    assert not repository.delete(ResourceUUID.generate())


def test_search_returns_stable_page() -> None:
    repository: ResourceRepository = InMemoryResourceRepository()
    high = make_resource(
        resource_uuid=ResourceUUID.from_string(
            "00000000-0000-0000-0000-000000000010"
        ),
        identifier=make_identifier("HIGH"),
    )
    low = make_resource(
        resource_uuid=ResourceUUID.from_string(
            "00000000-0000-0000-0000-000000000001"
        ),
        identifier=make_identifier("LOW"),
    )
    repository.save(high)
    repository.save(low)

    page = repository.search(
        ResourceSearchCriteria(
            limit=1,
            offset=1,
        )
    )

    assert page.total == 2
    assert page.limit == 1
    assert page.offset == 1
    assert page.items == (high,)


def test_repository_protocol_has_no_runtime_dependency() -> None:
    assert ResourceRepository.__module__ == (
        "eke.domain.repositories.resource_repository"
    )