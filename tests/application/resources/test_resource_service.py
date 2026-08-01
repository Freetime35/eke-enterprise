from __future__ import annotations

import pytest

from eke.application.resources import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    ResourceService,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import Resource, ResourceStatus
from eke.infrastructure.repositories import InMemoryResourceRepository
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def make_identifier(value: str = "32023R1114") -> BusinessIdentifier:
    return BusinessIdentifier(IdentifierScheme.CELEX, value)


def make_resource(
    *,
    resource_uuid: ResourceUUID | None = None,
    identifier_value: str = "32023R1114",
    status: ResourceStatus = ResourceStatus.UNKNOWN,
) -> Resource:
    return Resource(
        resource_uuid=resource_uuid or ResourceUUID.generate(),
        identifiers=(make_identifier(identifier_value),),
        status=status,
    )


def make_service() -> tuple[ResourceService, InMemoryResourceRepository]:
    repository = InMemoryResourceRepository()
    return (
        ResourceService(lambda: InMemoryUnitOfWork(repository)),
        repository,
    )


def test_create_persists_resource() -> None:
    service, repository = make_service()
    resource = make_resource()

    service.create(resource)

    assert repository.get(resource.resource_uuid) == resource


def test_create_rejects_duplicate_identity() -> None:
    service, _ = make_service()
    resource = make_resource()
    service.create(resource)

    with pytest.raises(ResourceAlreadyExistsError):
        service.create(resource)


def test_create_rejects_duplicate_identifier() -> None:
    service, _ = make_service()
    service.create(make_resource())

    with pytest.raises(ResourceAlreadyExistsError):
        service.create(make_resource())


def test_get_and_find_by_identifier() -> None:
    service, _ = make_service()
    resource = make_resource()
    service.create(resource)

    assert service.get(resource.resource_uuid) == resource
    assert service.find_by_identifier(resource.identifiers[0]) == resource


def test_missing_get_and_identifier_raise() -> None:
    service, _ = make_service()

    with pytest.raises(ResourceNotFoundError):
        service.get(ResourceUUID.generate())
    with pytest.raises(ResourceNotFoundError):
        service.find_by_identifier(make_identifier())


def test_update_replaces_existing_resource() -> None:
    service, _ = make_service()
    resource_uuid = ResourceUUID.generate()
    original = make_resource(resource_uuid=resource_uuid)
    replacement = make_resource(
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )
    service.create(original)

    service.update(replacement)

    assert service.get(resource_uuid) == replacement


def test_update_missing_resource_raises() -> None:
    service, _ = make_service()

    with pytest.raises(ResourceNotFoundError):
        service.update(make_resource())


def test_delete_and_exists() -> None:
    service, _ = make_service()
    resource = make_resource()
    service.create(resource)

    assert service.exists(resource.resource_uuid)
    service.delete(resource.resource_uuid)
    assert not service.exists(resource.resource_uuid)


def test_delete_missing_resource_raises() -> None:
    service, _ = make_service()

    with pytest.raises(ResourceNotFoundError):
        service.delete(ResourceUUID.generate())


def test_constructor_rejects_non_callable() -> None:
    with pytest.raises(TypeError, match="must be callable"):
        ResourceService(object())  # type: ignore[arg-type]


def test_invalid_arguments_are_rejected() -> None:
    service, _ = make_service()

    with pytest.raises(TypeError, match="resource must be a Resource"):
        service.create("invalid")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="resource_uuid must be a ResourceUUID"):
        service.get("invalid")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="identifier must be a BusinessIdentifier"):
        service.find_by_identifier("invalid")  # type: ignore[arg-type]
