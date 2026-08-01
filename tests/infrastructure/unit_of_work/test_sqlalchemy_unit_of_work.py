from __future__ import annotations

import pytest
from sqlalchemy.orm import Session, sessionmaker

from eke.application import UnitOfWork
from eke.domain.identity import BusinessIdentifier, IdentifierScheme, ResourceUUID
from eke.domain.resources import Resource
from eke.infrastructure.database import Base, create_session_factory, create_sqlite_engine
from eke.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@pytest.fixture
def factory() -> sessionmaker[Session]:
    engine = create_sqlite_engine()
    Base.metadata.create_all(engine)
    return create_session_factory(engine)


def make_resource() -> Resource:
    return Resource(
        ResourceUUID.generate(),
        (BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114"),),
    )


def test_satisfies_protocol(factory: sessionmaker[Session]) -> None:
    with SQLAlchemyUnitOfWork(factory) as uow:
        assert isinstance(uow, UnitOfWork)


def test_commit_persists_changes(factory: sessionmaker[Session]) -> None:
    resource = make_resource()

    with SQLAlchemyUnitOfWork(factory) as uow:
        uow.resources.save(resource)
        uow.commit()

    with SQLAlchemyUnitOfWork(factory) as uow:
        assert uow.resources.get(resource.resource_uuid) == resource


def test_missing_commit_rolls_back(factory: sessionmaker[Session]) -> None:
    resource = make_resource()

    with SQLAlchemyUnitOfWork(factory) as uow:
        uow.resources.save(resource)

    with SQLAlchemyUnitOfWork(factory) as uow:
        assert uow.resources.get(resource.resource_uuid) is None


def test_exception_rolls_back(factory: sessionmaker[Session]) -> None:
    resource = make_resource()

    with pytest.raises(RuntimeError):
        with SQLAlchemyUnitOfWork(factory) as uow:
            uow.resources.save(resource)
            raise RuntimeError("boom")

    with SQLAlchemyUnitOfWork(factory) as uow:
        assert uow.resources.get(resource.resource_uuid) is None


def test_commit_outside_context_raises(factory: sessionmaker[Session]) -> None:
    uow = SQLAlchemyUnitOfWork(factory)

    with pytest.raises(RuntimeError, match="not active"):
        uow.commit()
