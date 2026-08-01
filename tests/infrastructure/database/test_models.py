"""Tests for refined SQLAlchemy Resource mappings."""

from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.orm import Session, sessionmaker

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import Resource
from eke.infrastructure.database import (
    Base,
    create_session_factory,
    create_sqlite_engine,
)
from eke.infrastructure.database.models import (
    ResourceIdentifierModel,
    ResourceModel,
)
from eke.infrastructure.repositories import (
    SQLAlchemyResourceRepository,
)


def make_factory() -> sessionmaker[Session]:
    engine = create_sqlite_engine()
    Base.metadata.create_all(engine)
    return create_session_factory(engine)


def test_metadata_uses_deterministic_constraint_names() -> None:
    factory = make_factory()
    engine = factory.kw["bind"]
    inspector = inspect(engine)

    primary_key = inspector.get_pk_constraint("resources")
    assert primary_key["name"] == "pk_resources"

    foreign_keys = inspector.get_foreign_keys(
        "resource_identifiers"
    )
    assert foreign_keys[0]["name"] == (
        "fk_resource_identifiers_resource_uuid_resources"
    )


def test_resource_mapping_exposes_payload_metadata() -> None:
    factory = make_factory()
    resource = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )
    repository = SQLAlchemyResourceRepository(factory)
    repository.save(resource)

    with factory() as session:
        model = session.get(
            ResourceModel,
            str(resource.resource_uuid),
        )

        assert model is not None
        assert model.payload_version == 1
        assert model.created_at is not None
        assert model.updated_at is not None
        assert len(model.identifiers) == 1


def test_delete_cascades_identifier_rows() -> None:
    factory = make_factory()
    resource = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )
    repository = SQLAlchemyResourceRepository(factory)
    repository.save(resource)

    assert repository.delete(resource.resource_uuid)

    with factory() as session:
        assert session.query(
            ResourceIdentifierModel
        ).count() == 0
