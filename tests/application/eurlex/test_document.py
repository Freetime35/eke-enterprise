"""Tests for the transport-neutral EUR-Lex document."""

from datetime import UTC, datetime

import pytest

from eke.application.eurlex import EurLexDocument
from eke.domain.identity import CelexIdentifier


def test_document_accepts_timezone_aware_payload() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        content_type="application/rdf+xml",
        content=b"<rdf:RDF />",
        source_url=(
            "https://publications.europa.eu/"
            "resource/celex/32023R1114"
        ),
        retrieved_at=datetime(
            2026,
            8,
            1,
            12,
            0,
            tzinfo=UTC,
        ),
    )

    assert document.content == b"<rdf:RDF />"


def test_document_rejects_naive_timestamp() -> None:
    with pytest.raises(
        ValueError,
        match="retrieved_at must be timezone-aware",
    ):
        EurLexDocument(
            celex_identifier=CelexIdentifier.parse(
                "32023R1114"
            ),
            content_type="application/rdf+xml",
            content=b"<rdf:RDF />",
            source_url="https://example.test/document",
            retrieved_at=datetime(2026, 8, 1, 12, 0),
        )
