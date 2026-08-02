"""Tests for EUR-Lex metadata completeness assessment."""

from datetime import date

from eke.application.eurlex import (
    EurLexMetadata,
    EurLexOfficialJournalReference,
    EurLexTitle,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


def test_complete_metadata_has_full_score() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        titles=(
            EurLexTitle(
                LanguageCode("en"),
                "Markets in Crypto-assets",
            ),
        ),
        document_date=date(2023, 5, 31),
        publication_date=date(2023, 6, 9),
        languages=(LanguageCode("en"),),
        resource_type_uri=(
            "https://example.test/REG"
        ),
        status_uri=(
            "https://example.test/IN_FORCE"
        ),
        eli_uri="http://data.europa.eu/eli/reg/2023/1114/oj",
        cellar_uri=(
            "http://publications.europa.eu/"
            "resource/cellar/example"
        ),
        official_journal=(
            EurLexOfficialJournalReference(
                number="L 150",
                page_first="40",
                page_last="205",
            )
        ),
        responsible_agent_uris=(
            "http://publications.europa.eu/"
            "resource/authority/corporate-body/CONSIL",
        ),
    )

    report = metadata.assess_completeness()

    assert report.score == 1.0
    assert report.missing_fields == ()


def test_partial_metadata_reports_missing_fields() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        )
    )

    report = metadata.assess_completeness()

    assert report.score == 0.0
    assert "localized_title" in report.missing_fields
    assert "official_journal" in report.missing_fields
