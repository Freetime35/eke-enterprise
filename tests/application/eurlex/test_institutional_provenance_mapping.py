"""Tests for institution-derived canonical provenance."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexMetadata,
    EurLexTitle,
    institution_from_uri,
    resource_from_eurlex,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceSource,
)


def test_maps_financial_authority_provenance() -> None:
    retrieved_at = datetime(
        2026,
        8,
        2,
        12,
        0,
        tzinfo=UTC,
    )
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        content_type="application/rdf+xml",
        content=b"<rdf:RDF />",
        source_url="https://example.test/source",
        retrieved_at=retrieved_at,
    )
    metadata = EurLexMetadata(
        celex_identifier=document.celex_identifier,
        titles=(
            EurLexTitle(
                LanguageCode("en"),
                "Markets in Crypto-assets",
            ),
        ),
        institutions=(
            institution_from_uri(
                "http://publications.europa.eu/"
                "resource/authority/"
                "corporate-body/ECB"
            ),
            institution_from_uri(
                "http://publications.europa.eu/"
                "resource/authority/"
                "corporate-body/COM"
            ),
        ),
    )

    resource = resource_from_eurlex(
        document,
        metadata,
    )

    assert len(resource.provenance_records) == 2
    derived = resource.provenance_records[1]
    assert derived.source is ProvenanceSource.ECB
    assert (
        derived.acquisition_method
        is AcquisitionMethod.DERIVED
    )
