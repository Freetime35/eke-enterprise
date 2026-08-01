"""Tests for the EUR-Lex Resource import workflow."""

from __future__ import annotations

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexClient,
    EurLexDocument,
    EurLexMetadata,
    EurLexMetadataParser,
    EurLexResourceImportService,
    EurLexTitle,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0

    def fetch_document(
        self,
        celex_identifier: CelexIdentifier,
        *,
        accept: str = "application/rdf+xml",
    ) -> EurLexDocument:
        self.calls += 1
        assert accept == "application/rdf+xml"
        return EurLexDocument(
            celex_identifier=celex_identifier,
            content_type="application/rdf+xml",
            content=b"<rdf:RDF />",
            source_url=(
                "https://publications.europa.eu/"
                f"resource/celex/{celex_identifier}"
            ),
            retrieved_at=NOW,
        )


class FakeParser:
    def __init__(self) -> None:
        self.calls = 0

    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        self.calls += 1
        return EurLexMetadata(
            celex_identifier=document.celex_identifier,
            titles=(
                EurLexTitle(
                    LanguageCode("en"),
                    "Imported title",
                ),
            ),
            resource_type_uri=(
                "https://example.test/REG"
            ),
            status_uri=(
                "https://example.test/IN_FORCE"
            ),
        )


def make_service() -> tuple[
    EurLexResourceImportService,
    FakeClient,
    FakeParser,
    InMemoryResourceRepository,
]:
    repository = InMemoryResourceRepository()
    client = FakeClient()
    parser = FakeParser()

    assert isinstance(client, EurLexClient)
    assert isinstance(parser, EurLexMetadataParser)

    service = EurLexResourceImportService(
        client=client,
        parser=parser,
        unit_of_work_factory=(
            lambda: InMemoryUnitOfWork(repository)
        ),
    )
    return service, client, parser, repository


def test_import_creates_and_persists_resource() -> None:
    service, client, parser, repository = make_service()
    celex = CelexIdentifier.parse("32023R1114")

    result = service.import_resource(celex)

    assert result.created
    assert result.resource.identifiers == (
        celex.to_business_identifier(),
    )
    assert repository.count() == 1
    assert client.calls == 1
    assert parser.calls == 1


def test_import_is_idempotent_without_external_refetch() -> None:
    service, client, parser, repository = make_service()
    celex = CelexIdentifier.parse("32023R1114")

    first = service.import_resource(celex)
    second = service.import_resource(celex)

    assert first.created
    assert not second.created
    assert second.resource == first.resource
    assert repository.count() == 1
    assert client.calls == 1
    assert parser.calls == 1
