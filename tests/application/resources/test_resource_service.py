"""Tests for ResourceService."""

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
        status=status,
    )


def make_service() -> ResourceService:
    return ResourceService(InMemoryResourceRepository())


def test_create_persists_resource() -> None:
    service = make_service()
    resource = make_resource()

    service.create(resource)

    assert service.get(resource.resource_uuid) == resource


def test_create_rejects_duplicate_identity() -> None:
    service = make_service()
    resource = make_resource()
    service.create(resource)

    with pytest.raises(
        ResourceAlreadyExistsError,
        match="resource already exists",
    ):
        service.create(resource)


def test_create_rejects_duplicate_business_identifier() -> None:
    service = make_service()
    first = make_resource(identifier_value="32023R1114")
    second = make_resource(identifier_value="32023R1114")
    service.create(first)

    with pytest.raises(
        ResourceAlreadyExistsError,
        match="business identifier",
    ):
        service.create(second)


def test_get_returns_resource() -> None:
    service = make_service()
    resource = make_resource()
    service.create(resource)

    assert service.get(resource.resource_uuid) == resource


def test_get_raises_when_missing() -> None:
    service = make_service()
    resource_uuid = ResourceUUID.generate()

    with pytest.raises(
        ResourceNotFoundError,
        match="resource not found",
    ):
        service.get(resource_uuid)


def test_find_by_identifier_returns_resource() -> None:
    service = make_service()
    identifier = make_identifier()
    resource = Resource(
        ResourceUUID.generate(),
        (identifier,),
    )
    service.create(resource)

    assert service.find_by_identifier(identifier) == resource


def test_find_by_identifier_raises_when_missing() -> None:
    service = make_service()

    with pytest.raises(
        ResourceNotFoundError,
        match="business identifier",
    ):
        service.find_by_identifier(make_identifier())


def test_update_replaces_existing_resource() -> None:
    service = make_service()
    resource_uuid = ResourceUUID.generate()
    original = make_resource(
        resource_uuid=resource_uuid,
        status=ResourceStatus.PUBLISHED,
    )
    replacement = make_resource(
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )
    service.create(original)

    service.update(replacement)

    assert service.get(resource_uuid) == replacement


def test_update_raises_when_resource_missing() -> None:
    service = make_service()
    resource = make_resource()

    with pytest.raises(
        ResourceNotFoundError,
        match="resource not found",
    ):
        service.update(resource)


def test_update_rejects_identifier_owned_by_another_resource() -> None:
    service = make_service()
    shared_identifier = "32023R1114"
    first = make_resource(identifier_value=shared_identifier)
    second = make_resource(identifier_value="32013R0575")
    service.create(first)
    service.create(second)

    conflicting_update = Resource(
        resource_uuid=second.resource_uuid,
        identifiers=(make_identifier(shared_identifier),),
        status=second.status,
    )

    with pytest.raises(
        ResourceAlreadyExistsError,
        match="another resource",
    ):
        service.update(conflicting_update)


def test_delete_removes_resource() -> None:
    service = make_service()
    resource = make_resource()
    service.create(resource)

    service.delete(resource.resource_uuid)

    assert not service.exists(resource.resource_uuid)


def test_delete_raises_when_missing() -> None:
    service = make_service()

    with pytest.raises(
        ResourceNotFoundError,
        match="resource not found",
    ):
        service.delete(ResourceUUID.generate())


def test_exists_reports_presence() -> None:
    service = make_service()
    resource = make_resource()

    assert not service.exists(resource.resource_uuid)

    service.create(resource)

    assert service.exists(resource.resource_uuid)


def test_constructor_rejects_invalid_repository() -> None:
    with pytest.raises(
        TypeError,
        match="repository must satisfy ResourceRepository",
    ):
        ResourceService(object())  # type: ignore[arg-type]


def test_resource_arguments_are_validated() -> None:
    service = make_service()

    with pytest.raises(
        TypeError,
        match="resource must be a Resource",
    ):
        service.create("invalid")  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match="resource must be a Resource",
    ):
        service.update("invalid")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "method_name",
    ["get", "delete", "exists"],
)
def test_resource_uuid_arguments_are_validated(
    method_name: str,
) -> None:
    service = make_service()
    method = getattr(service, method_name)

    with pytest.raises(
        TypeError,
        match="resource_uuid must be a ResourceUUID",
    ):
        method("invalid")


def test_identifier_argument_is_validated() -> None:
    service = make_service()

    with pytest.raises(
        TypeError,
        match="identifier must be a BusinessIdentifier",
    ):
        service.find_by_identifier(  # type: ignore[arg-type]
            "CELEX:32023R1114"
        )
