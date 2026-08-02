"""Tests for legal bases on EUR-Lex metadata."""

import pytest

from eke.application.eurlex import (
    EurLexLegalBasis,
    EurLexLegalBasisKind,
    EurLexMetadata,
)
from eke.domain.identity import CelexIdentifier


def test_metadata_accepts_legal_bases() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        legal_bases=(
            EurLexLegalBasis(
                kind=(
                    EurLexLegalBasisKind
                    .TREATY_ARTICLE
                ),
                target_uri=(
                    "http://data.europa.eu/eli/"
                    "treaty/tfeu_2012/art_114/oj"
                ),
                source_predicate=(
                    "work_based_on_treaty"
                ),
            ),
        ),
    )

    assert len(metadata.legal_bases) == 1


def test_metadata_rejects_invalid_legal_bases() -> None:
    with pytest.raises(
        TypeError,
        match="legal_bases",
    ):
        EurLexMetadata(
            celex_identifier=CelexIdentifier.parse(
                "32023R1114"
            ),
            legal_bases=(
                "Article 114",  # type: ignore[arg-type]
            ),
        )
