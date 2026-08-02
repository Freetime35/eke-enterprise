"""Tests for complete EUR-Lex aggregate enrichment."""

from datetime import UTC, date, datetime

from eke.application.eurlex import (
    EurLexClassification,
    EurLexDocument,
    EurLexMetadata,
    EurLexRelationship,
    EurLexResourceImportService,
    EurLexTitle,
    FinancialClassificationCategory,
)
from eke.domain.identity import (
    CelexIdentifier,
    ResourceUUID,
)
from eke.domain.localization import LanguageCode
from eke.domain.relationships import RelationshipType
from eke.domain.resources import Resource
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


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
            retrieved_at=datetime(
                2026,
                8,
                1,
                12,
                0,
                tzinfo=UTC,
            ),
        )


class Parser:
    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        return EurLexMetadata(
            celex_identifier=document.celex_identifier,
            titles=(
                EurLexTitle(
                    LanguageCode("en"),
                    "Imported regulation",
                ),
            ),
            document_date=date(2023, 5, 31),
            entry_into_force_date=date(2023, 6, 29),
            status_uri="https://example.test/IN_FORCE",
            resource_type_uri="https://example.test/REG",
            classifications=(
                EurLexClassification(
                    uri="http://eurovoc.europa.eu/1001",
                    code="1001",
                    language=LanguageCode("en"),
                    label="financial market",
                    financial_category=(
                        FinancialClassificationCategory
                        .CAPITAL_MARKETS
                    ),
                ),
            ),
            relationships=(
                EurLexRelationship(
                    target_celex=CelexIdentifier.parse(
                        "32013R0575"
                    ),
                    relationship_type=(
                        RelationshipType.AMENDS
                    ),
                ),
            ),
        )


def test_full_import_enriches_owned_aggregate_values() -> None:
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
        Parser(),
        lambda: InMemoryUnitOfWork(repository),
    )

    result = service.import_resource(
        CelexIdentifier.parse("32023R1114")
    )

    assert result.created
    assert len(result.resource.versions) == 1
    assert len(result.resource.relationships) == 1
    assert len(result.resource.classifications) == 1
    assert len(result.resource.provenance_records) == 1
    assert repository.count() == 2

    relationship = result.resource.relationships[0]
    assert relationship.target == target.resource_uuid
    assert (
        relationship.relationship_type
        is RelationshipType.AMENDS
    )

    classification = result.resource.classifications[0]
    assert classification.code == "1001"
    assert classification.label.value == "financial market"
    assert classification.label.language == LanguageCode("en")

    persisted_target = repository.get_by_identifier(
        target_celex.to_business_identifier()
    )
    assert persisted_target == target