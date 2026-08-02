"""Tests for resolved EUR-Lex relationship import."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexMetadata,
    EurLexRelationship,
    EurLexResourceImportService,
)
from eke.domain.identity import (
    CelexIdentifier,
    ResourceUUID,
)
from eke.domain.relationships import RelationshipType
from eke.domain.resources import Resource
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import (
    InMemoryUnitOfWork,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class Client:
    def fetch_document(
        self,
        celex_identifier: CelexIdentifier,
        *,
        accept: str = "application/rdf+xml",
    ) -> EurLexDocument:
        return EurLexDocument(
            celex_identifier=celex_identifier,
            content_type=accept,
            content=b"<rdf:RDF />",
            source_url="https://example.test/source",
            retrieved_at=NOW,
        )


class Parser:
    def __init__(
        self,
        target: CelexIdentifier,
    ) -> None:
        self._target = target

    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        return EurLexMetadata(
            celex_identifier=(
                document.celex_identifier
            ),
            relationships=(
                EurLexRelationship(
                    target_celex=self._target,
                    relationship_type=(
                        RelationshipType.AMENDS
                    ),
                ),
                EurLexRelationship(
                    target_celex=self._target,
                    relationship_type=(
                        RelationshipType.AMENDS
                    ),
                ),
            ),
        )


def test_imports_only_resolved_relationships() -> None:
    repository = InMemoryResourceRepository()
    target_celex = CelexIdentifier.parse(
        "32013R0575"
    )
    target = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(
            target_celex.to_business_identifier(),
        ),
    )
    repository.save(target)

    service = EurLexResourceImportService(
        Client(),
        Parser(target_celex),
        lambda: InMemoryUnitOfWork(repository),
    )

    result = service.import_resource(
        CelexIdentifier.parse("32023R1114")
    )

    assert len(result.resource.relationships) == 1
    relationship = result.resource.relationships[0]
    assert relationship.target == target.resource_uuid
    assert (
        relationship.relationship_type
        is RelationshipType.AMENDS
    )
    assert repository.count() == 2


def test_unresolved_target_does_not_create_stub() -> None:
    repository = InMemoryResourceRepository()
    target_celex = CelexIdentifier.parse(
        "32013R0575"
    )
    service = EurLexResourceImportService(
        Client(),
        Parser(target_celex),
        lambda: InMemoryUnitOfWork(repository),
    )

    result = service.import_resource(
        CelexIdentifier.parse("32023R1114")
    )

    assert result.resource.relationships == ()
    assert repository.count() == 1
    assert (
        repository.get_by_identifier(
            target_celex.to_business_identifier()
        )
        is None
    )
