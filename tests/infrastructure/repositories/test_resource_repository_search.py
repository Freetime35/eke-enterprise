"""Repository search contract tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from sqlalchemy.orm import Session, sessionmaker

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.repositories import (
    ResourceRepository,
    ResourceSearchCriteria,
)
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceType,
)
from eke.infrastructure.database import (
    Base,
    create_session_factory,
    create_sqlite_engine,
)
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
    SQLAlchemyResourceRepository,
)


def make_resource(
    *,
    uuid_value: str,
    identifier_scheme: IdentifierScheme,
    identifier_value: str,
    resource_type: ResourceType,
    status: ResourceStatus,
) -> Resource:
    return Resource(
        resource_uuid=ResourceUUID.from_string(
            uuid_value
        ),
        identifiers=(
            BusinessIdentifier(
                identifier_scheme,
                identifier_value,
            ),
        ),
        resource_type=resource_type,
        status=status,
    )


def repository_factories() -> tuple[
    Callable[[], ResourceRepository],
    ...,
]:
    def in_memory() -> ResourceRepository:
        return InMemoryResourceRepository()

    def sqlalchemy_repository() -> ResourceRepository:
        engine = create_sqlite_engine()
        Base.metadata.create_all(engine)
        factory: sessionmaker[Session] = (
            create_session_factory(engine)
        )
        return SQLAlchemyResourceRepository(factory)

    return (in_memory, sqlalchemy_repository)


@pytest.mark.parametrize(
    "repository_factory",
    repository_factories(),
)
def test_search_filters_and_paginates(
    repository_factory: Callable[
        [],
        ResourceRepository,
    ],
) -> None:
    repository = repository_factory()
    resources = (
        make_resource(
            uuid_value=(
                "00000000-0000-0000-0000-000000000001"
            ),
            identifier_scheme=IdentifierScheme.CELEX,
            identifier_value="A",
            resource_type=ResourceType.REGULATION,
            status=ResourceStatus.IN_FORCE,
        ),
        make_resource(
            uuid_value=(
                "00000000-0000-0000-0000-000000000002"
            ),
            identifier_scheme=IdentifierScheme.CELEX,
            identifier_value="B",
            resource_type=ResourceType.REGULATION,
            status=ResourceStatus.IN_FORCE,
        ),
        make_resource(
            uuid_value=(
                "00000000-0000-0000-0000-000000000003"
            ),
            identifier_scheme=IdentifierScheme.ELI,
            identifier_value="C",
            resource_type=ResourceType.DIRECTIVE,
            status=ResourceStatus.REPEALED,
        ),
    )
    for resource in resources:
        repository.save(resource)

    page = repository.search(
        ResourceSearchCriteria(
            identifier_scheme=IdentifierScheme.CELEX,
            resource_type=ResourceType.REGULATION,
            status=ResourceStatus.IN_FORCE,
            limit=1,
            offset=1,
        )
    )

    assert page.total == 2
    assert page.limit == 1
    assert page.offset == 1
    assert page.items == (resources[1],)


@pytest.mark.parametrize(
    "repository_factory",
    repository_factories(),
)
def test_search_order_is_stable_by_uuid(
    repository_factory: Callable[
        [],
        ResourceRepository,
    ],
) -> None:
    repository = repository_factory()
    high = make_resource(
        uuid_value=(
            "00000000-0000-0000-0000-000000000010"
        ),
        identifier_scheme=IdentifierScheme.CELEX,
        identifier_value="HIGH",
        resource_type=ResourceType.REGULATION,
        status=ResourceStatus.IN_FORCE,
    )
    low = make_resource(
        uuid_value=(
            "00000000-0000-0000-0000-000000000001"
        ),
        identifier_scheme=IdentifierScheme.CELEX,
        identifier_value="LOW",
        resource_type=ResourceType.REGULATION,
        status=ResourceStatus.IN_FORCE,
    )
    repository.save(high)
    repository.save(low)

    page = repository.search(
        ResourceSearchCriteria()
    )

    assert page.items == (low, high)
