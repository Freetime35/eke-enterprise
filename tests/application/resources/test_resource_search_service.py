"""Tests for ResourceService search."""

from __future__ import annotations

from eke.application.resources import ResourceService
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.repositories import ResourceSearchCriteria
from eke.domain.resources import Resource
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def test_service_delegates_search_to_repository() -> None:
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
    service = ResourceService(
        lambda: InMemoryUnitOfWork(repository)
    )

    page = service.search(ResourceSearchCriteria())

    assert page.items == (resource,)
    assert page.total == 1
