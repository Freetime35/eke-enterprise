"""Tests for EUR-Lex metadata to Resource mapping."""

from datetime import UTC, date, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexMetadata,
    EurLexTitle,
    map_resource_status,
    map_resource_type,
    resource_from_eurlex,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceSource,
)
from eke.domain.resources import (
    ResourceStatus,
    ResourceType,
)

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


def make_document() -> EurLexDocument:
    return EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        content_type="application/rdf+xml",
        content=b"<rdf:RDF />",
        source_url=(
            "https://publications.europa.eu/"
            "resource/celex/32023R1114"
        ),
        retrieved_at=NOW,
    )


def make_metadata() -> EurLexMetadata:
    return EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        titles=(
            EurLexTitle(
                LanguageCode("en"),
                "Markets in Crypto-assets",
            ),
            EurLexTitle(
                LanguageCode("fr"),
                "Marchés de crypto-actifs",
            ),
            EurLexTitle(None, "Unlabelled title"),
        ),
        entry_into_force_date=date(2023, 6, 29),
        resource_type_uri=(
            "http://publications.europa.eu/"
            "resource/authority/resource-type/REG"
        ),
        status_uri=(
            "http://publications.europa.eu/"
            "resource/authority/resource-status/IN_FORCE"
        ),
        eurovoc_concept_uris=(
            "http://eurovoc.europa.eu/1001",
        ),
    )


def test_resource_from_eurlex_maps_core_fields() -> None:
    resource = resource_from_eurlex(
        make_document(),
        make_metadata(),
    )

    assert resource.identifiers[0].value == "32023R1114"
    assert resource.resource_type is ResourceType.REGULATION
    assert resource.status is ResourceStatus.IN_FORCE
    assert tuple(
        title.language
        for title in resource.titles
    ) == (
        LanguageCode("en"),
        LanguageCode("fr"),
    )
    assert len(resource.provenance_records) == 1
    provenance = resource.provenance_records[0]
    assert provenance.source is ProvenanceSource.EUR_LEX
    assert (
        provenance.acquisition_method
        is AcquisitionMethod.API
    )
    assert provenance.checksum is not None
    assert provenance.checksum.startswith("sha256:")
    assert resource.classifications == ()


def test_type_mapping_uses_celex_fallback() -> None:
    assert (
        map_resource_type(None, "L", "3")
        is ResourceType.DIRECTIVE
    )
    assert (
        map_resource_type(None, "CJ", "6")
        is ResourceType.CASE_LAW
    )


def test_unknown_source_values_remain_conservative() -> None:
    assert (
        map_resource_type(
            "https://example.test/UNKNOWN",
            "ZZ",
            "3",
        )
        is ResourceType.OTHER
    )
    assert (
        map_resource_status(
            "https://example.test/UNKNOWN"
        )
        is ResourceStatus.UNKNOWN
    )
