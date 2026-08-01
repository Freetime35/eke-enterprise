from datetime import date

import pytest

from eke.application.resources import (
    ResourceRelationshipAlreadyExistsError,
    ResourceRelationshipConflictError,
    ResourceRelationshipNotFoundError,
    ResourceRelationshipService,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.relationships import (
    RelationshipType,
    ResourceRelationship,
)
from eke.domain.resources import Resource
from eke.domain.temporal import ValidityPeriod
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def make_service() -> tuple[
    ResourceRelationshipService,
    Resource,
    Resource,
]:
    repository = InMemoryResourceRepository()
    source = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "SOURCE",
            ),
        ),
    )
    target = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "TARGET",
            ),
        ),
    )
    repository.save(source)
    repository.save(target)
    service = ResourceRelationshipService(
        lambda: InMemoryUnitOfWork(repository)
    )
    return service, source, target


def make_relationship(
    source: Resource,
    target: Resource,
) -> ResourceRelationship:
    return ResourceRelationship(
        source=source.resource_uuid,
        target=target.resource_uuid,
        relationship_type=RelationshipType.AMENDS,
        validity=ValidityPeriod(
            date(2024, 1, 1),
            None,
        ),
    )


def test_add_and_list_relationship() -> None:
    service, source, target = make_service()
    relationship = make_relationship(source, target)

    service.add(source.resource_uuid, relationship)

    assert service.list(source.resource_uuid) == (
        relationship,
    )


def test_duplicate_relationship_is_rejected() -> None:
    service, source, target = make_service()
    relationship = make_relationship(source, target)
    service.add(source.resource_uuid, relationship)

    with pytest.raises(
        ResourceRelationshipAlreadyExistsError
    ):
        service.add(source.resource_uuid, relationship)


def test_missing_target_is_rejected() -> None:
    service, source, _ = make_service()
    relationship = ResourceRelationship(
        source=source.resource_uuid,
        target=ResourceUUID.generate(),
        relationship_type=RelationshipType.CITES,
    )

    with pytest.raises(ResourceRelationshipConflictError):
        service.add(source.resource_uuid, relationship)


def test_remove_missing_relationship_is_rejected() -> None:
    service, source, target = make_service()

    with pytest.raises(
        ResourceRelationshipNotFoundError
    ):
        service.remove(
            source.resource_uuid,
            target.resource_uuid,
            RelationshipType.AMENDS,
            date(2024, 1, 1),
            None,
        )
