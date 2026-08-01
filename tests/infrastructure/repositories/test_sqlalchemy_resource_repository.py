from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from eke.domain.classification import ClassificationConcept, ClassificationScheme
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
    ResourceVersionUUID,
)
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.provenance import AcquisitionMethod, ProvenanceRecord, ProvenanceSource
from eke.domain.relationships import RelationshipType, ResourceRelationship
from eke.domain.repositories import ResourceRepository
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceTitle,
    ResourceType,
    ResourceVersion,
)
from eke.domain.temporal import ValidityPeriod
from eke.infrastructure.database import (
    Base,
    create_session_factory,
    create_sqlite_engine,
)
from eke.infrastructure.repositories import SQLAlchemyResourceRepository


@pytest.fixture
def factory() -> sessionmaker[Session]:
    engine = create_sqlite_engine()
    Base.metadata.create_all(engine)
    return create_session_factory(engine)


@pytest.fixture
def repository(
    factory: sessionmaker[Session],
) -> SQLAlchemyResourceRepository:
    return SQLAlchemyResourceRepository(factory)


def make_resource() -> Resource:
    resource_uuid = ResourceUUID.generate()
    first_version = ResourceVersion(
        ResourceVersionUUID.generate(),
        resource_uuid,
        ResourceStatus.SUPERSEDED,
        ValidityPeriod(date(2020, 1, 1), date(2023, 12, 31)),
    )
    current_version = ResourceVersion(
        ResourceVersionUUID.generate(),
        resource_uuid,
        ResourceStatus.IN_FORCE,
        ValidityPeriod(date(2024, 1, 1), None),
        first_version.version_uuid,
    )
    return Resource(
        resource_uuid=resource_uuid,
        identifiers=(
            BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114"),
            BusinessIdentifier(
                IdentifierScheme.ELI,
                "http://data.europa.eu/eli/reg/2023/1114/oj",
            ),
        ),
        resource_type=ResourceType.REGULATION,
        status=ResourceStatus.IN_FORCE,
        titles=(
            ResourceTitle(
                LocalizedText(LanguageCode("en"), "Markets in Crypto-assets"),
            ),
        ),
        versions=(first_version, current_version),
        relationships=(
            ResourceRelationship(
                resource_uuid,
                ResourceUUID.generate(),
                RelationshipType.AMENDS,
            ),
        ),
        provenance_records=(
            ProvenanceRecord(
                resource_uuid,
                ProvenanceSource.EUR_LEX,
                "CELEX:32023R1114",
                datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
                AcquisitionMethod.API,
                "sha256:abc",
            ),
        ),
        classifications=(
            ClassificationConcept(
                ClassificationScheme.EUROVOC,
                "2406",
                LocalizedText(LanguageCode("en"), "Financial relations"),
            ),
        ),
    )


def test_repository_satisfies_protocol(
    repository: SQLAlchemyResourceRepository,
) -> None:
    assert isinstance(repository, ResourceRepository)


def test_round_trip_preserves_complete_aggregate(
    repository: SQLAlchemyResourceRepository,
) -> None:
    resource = make_resource()

    repository.save(resource)

    assert repository.get(resource.resource_uuid) == resource


def test_save_replaces_existing_aggregate(
    repository: SQLAlchemyResourceRepository,
) -> None:
    resource = make_resource()
    repository.save(resource)
    replacement = Resource(
        resource_uuid=resource.resource_uuid,
        identifiers=resource.identifiers,
        resource_type=resource.resource_type,
        status=ResourceStatus.REPEALED,
    )

    repository.save(replacement)

    assert repository.get(resource.resource_uuid) == replacement


def test_lookup_by_business_identifier(
    repository: SQLAlchemyResourceRepository,
) -> None:
    resource = make_resource()
    repository.save(resource)

    for identifier in resource.identifiers:
        assert repository.get_by_identifier(identifier) == resource


def test_missing_lookups_return_none(
    repository: SQLAlchemyResourceRepository,
) -> None:
    assert repository.get(ResourceUUID.generate()) is None
    assert (
        repository.get_by_identifier(
            BusinessIdentifier(IdentifierScheme.CELEX, "missing")
        )
        is None
    )


def test_exists_and_delete(
    repository: SQLAlchemyResourceRepository,
) -> None:
    resource = make_resource()
    repository.save(resource)

    assert repository.exists(resource.resource_uuid)
    assert repository.delete(resource.resource_uuid)
    assert not repository.exists(resource.resource_uuid)
    assert not repository.delete(resource.resource_uuid)


def test_duplicate_business_identifier_is_rejected(
    repository: SQLAlchemyResourceRepository,
) -> None:
    first = make_resource()
    repository.save(first)
    duplicate = Resource(
        ResourceUUID.generate(),
        (first.identifiers[0],),
    )

    with pytest.raises(
        ValueError,
        match="business identifier already belongs",
    ):
        repository.save(duplicate)


def test_invalid_public_inputs_are_rejected(
    repository: SQLAlchemyResourceRepository,
) -> None:
    with pytest.raises(TypeError, match="resource must be a Resource"):
        repository.save("invalid")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="resource_uuid must be a ResourceUUID"):
        repository.get("invalid")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="identifier must be a BusinessIdentifier"):
        repository.get_by_identifier("invalid")  # type: ignore[arg-type]
