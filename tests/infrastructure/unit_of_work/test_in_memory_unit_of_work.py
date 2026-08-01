from __future__ import annotations

import pytest

from eke.application import UnitOfWork
from eke.domain.identity import BusinessIdentifier, IdentifierScheme, ResourceUUID
from eke.domain.resources import Resource
from eke.infrastructure.repositories import InMemoryResourceRepository
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def make_resource() -> Resource:
    return Resource(
        ResourceUUID.generate(),
        (BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114"),),
    )


def test_satisfies_protocol() -> None:
    assert isinstance(InMemoryUnitOfWork(), UnitOfWork)


def test_commit_preserves_changes() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource()

    with InMemoryUnitOfWork(repository) as uow:
        uow.resources.save(resource)
        uow.commit()

    assert repository.exists(resource.resource_uuid)


def test_missing_commit_rolls_back() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource()

    with InMemoryUnitOfWork(repository) as uow:
        uow.resources.save(resource)

    assert not repository.exists(resource.resource_uuid)


def test_exception_rolls_back() -> None:
    repository = InMemoryResourceRepository()
    resource = make_resource()

    with pytest.raises(RuntimeError):
        with InMemoryUnitOfWork(repository) as uow:
            uow.resources.save(resource)
            raise RuntimeError("boom")

    assert not repository.exists(resource.resource_uuid)
