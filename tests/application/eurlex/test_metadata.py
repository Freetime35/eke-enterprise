"""Tests for transport-neutral EUR-Lex metadata."""

from datetime import date

import pytest

from eke.application.eurlex import (
    EurLexMetadata,
    EurLexTitle,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


def test_metadata_accepts_stable_fields() -> None:
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
        languages=(LanguageCode("en"),),
        resource_type_uri="http://example.test/regulation",
        eurovoc_concept_uris=(
            "http://eurovoc.europa.eu/1001",
        ),
    )

    assert metadata.document_date == date(2023, 5, 31)
    assert metadata.titles[0].language == LanguageCode("en")


def test_title_normalizes_whitespace() -> None:
    title = EurLexTitle(
        LanguageCode("en"),
        "  Markets   in Crypto-assets  ",
    )

    assert title.value == "Markets in Crypto-assets"


def test_title_rejects_empty_value() -> None:
    with pytest.raises(
        ValueError,
        match="value must not be empty",
    ):
        EurLexTitle(LanguageCode("en"), "  ")
