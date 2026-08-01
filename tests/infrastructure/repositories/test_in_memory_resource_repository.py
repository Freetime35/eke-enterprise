"""Tests for InMemoryResourceRepository."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.repositories import ResourceRepository
from eke.domain.resources import Resource, ResourceStatus, ResourceType
from eke.infrastructure.repositories import InMemoryResourceRepository


def make_identifier(
    value: str = "32023R1114",
) -> BusinessIdentifier:
    return BusinessIdentifier(
        IdentifierScheme.CELEX,
        value,
    )


def make_resource(
    *,
    resource_uuid: ResourceUUID | None = None,
    identifier_value: str = "32023R1114",
    status: ResourceStatus = ResourceStatus.UNKNOWN,
) -> Resource:
    return Resource(
        resource_uuid=resource_uuid or ResourceUUID.generate(),
        identifiers=(make_identifier(identifier_value),),
        resource_type=ResourceType.REGULATION,
        status=status,
    )


def test_repository_satisfies_domain_protocol() -> None:
    repository = InMemoryResourceRepository()

    assert isinstance(repository, ResourceRepository)


def test_repository_starts_empty() -> None:
    repository = InMemoryResourceRepository()

    assert repository.count() == 0


def test_save_and_get_resource() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource()

    repository.save(resource)

    assert repository.get(resource.resource_uuid) == resource
    assert repository.count() == 1


def test_save_replaces_existing_resource() -> None:
    repository = InMemoryResourceRepository()
    resource_uuid = ResourceUUID.generate()
    original = make_resource(
        resource_uuid=resource_uuid,
        status=ResourceStatus.PUBLISHED,
    )
    replacement = make_resource(
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )

    repository.save(original)
    repository.save(replacement)

    assert repository.get(resource_uuid) == replacement
    assert repository.count() == 1


def test_get_returns_none_for_missing_resource() -> None:
    repository = InMemoryResourceRepository()

    assert repository.get(ResourceUUID.generate()) is None


def test_get_by_identifier_returns_matching_resource() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource(identifier_value="32023R1114")
    repository.save(resource)

    assert repository.get_by_identifier(
        make_identifier("32023R1114")
    ) == resource


def test_get_by_identifier_returns_none_when_missing() -> None:
    repository = InMemoryResourceRepository()

    assert repository.get_by_identifier(
        make_identifier("32023R1114")
    ) is None


def test_exists_reports_presence() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource()

    assert not repository.exists(resource.resource_uuid)

    repository.save(resource)

    assert repository.exists(resource.resource_uuid)


def test_delete_existing_resource() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource()
    repository.save(resource)

    assert repository.delete(resource.resource_uuid)
    assert repository.get(resource.resource_uuid) is None
    assert repository.count() == 0


def test_delete_missing_resource_returns_false() -> None:
    repository = InMemoryResourceRepository()

    assert not repository.delete(ResourceUUID.generate())


def test_clear_removes_all_resources() -> None:
    repository = InMemoryResourceRepository()
    repository.save(make_resource(identifier_value="32023R1114"))
    repository.save(make_resource(identifier_value="32013R0575"))

    repository.clear()

    assert repository.count() == 0


def test_save_rejects_invalid_resource_type() -> None:
    repository = InMemoryResourceRepository()

    with pytest.raises(
        TypeError,
        match="resource must be a Resource",
    ):
        repository.save("invalid")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "method_name",
    ["get", "exists", "delete"],
)
def test_uuid_methods_reject_invalid_type(
    method_name: str,
) -> None:
    repository = InMemoryResourceRepository()
    method = getattr(repository, method_name)

    with pytest.raises(
        TypeError,
        match="resource_uuid must be a ResourceUUID",
    ):
        method("invalid")


def test_get_by_identifier_rejects_invalid_type() -> None:
    repository = InMemoryResourceRepository()

    with pytest.raises(
        TypeError,
        match="identifier must be a BusinessIdentifier",
    ):
        repository.get_by_identifier(  # type: ignore[arg-type]
            "CELEX:32023R1114"
        )


def test_repository_instances_do_not_share_state() -> None:
    first = InMemoryResourceRepository()
    second = InMemoryResourceRepository()
    resource = make_resource()

    first.save(resource)

    assert first.exists(resource.resource_uuid)
    assert not second.exists(resource.resource_uuid)


def test_concurrent_saves_are_safe() -> None:
    repository = InMemoryResourceRepository()
    resources = tuple(
        make_resource(identifier_value=f"32023R{index:04d}")
        for index in range(50)
    )

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(repository.save, resources))

    assert repository.count() == len(resources)
    assert all(
        repository.exists(resource.resource_uuid)
        for resource in resources
    )
