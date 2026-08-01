from datetime import date

import pytest

from eke.application.resources import (
    ResourceVersionConflictError,
    ResourceVersionNotFoundError,
    ResourceVersionService,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
    ResourceVersionUUID,
)
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceVersion,
)
from eke.domain.temporal import ValidityPeriod
from eke.infrastructure.repositories import InMemoryResourceRepository
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def make_service() -> tuple[
    ResourceVersionService,
    Resource,
]:
    repository = InMemoryResourceRepository()
    resource = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )
    repository.save(resource)
    return (
        ResourceVersionService(
            lambda: InMemoryUnitOfWork(repository)
        ),
        resource,
    )


def make_version(
    resource_uuid: ResourceUUID,
    previous: ResourceVersionUUID | None = None,
) -> ResourceVersion:
    return ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
        validity=ValidityPeriod(date(2024, 1, 1), None),
        previous_version_uuid=previous,
    )


def test_add_list_and_get_version() -> None:
    service, resource = make_service()
    version = make_version(resource.resource_uuid)

    service.add(resource.resource_uuid, version)

    assert service.list(resource.resource_uuid) == (version,)
    assert service.get(
        resource.resource_uuid,
        version.version_uuid,
    ) == version


def test_missing_previous_version_is_rejected() -> None:
    service, resource = make_service()
    version = make_version(
        resource.resource_uuid,
        ResourceVersionUUID.generate(),
    )

    with pytest.raises(ResourceVersionConflictError):
        service.add(resource.resource_uuid, version)


def test_referenced_version_cannot_be_removed() -> None:
    service, resource = make_service()
    first = make_version(resource.resource_uuid)
    second = make_version(
        resource.resource_uuid,
        first.version_uuid,
    )
    service.add(resource.resource_uuid, first)
    service.add(resource.resource_uuid, second)

    with pytest.raises(ResourceVersionConflictError):
        service.remove(
            resource.resource_uuid,
            first.version_uuid,
        )


def test_missing_version_is_rejected() -> None:
    service, resource = make_service()

    with pytest.raises(ResourceVersionNotFoundError):
        service.get(
            resource.resource_uuid,
            ResourceVersionUUID.generate(),
        )
