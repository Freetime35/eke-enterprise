"""Tests for legal references on EUR-Lex metadata."""

import pytest

from eke.application.eurlex import (
    EurLexLegalReference,
    EurLexLegalReferenceKind,
    EurLexMetadata,
)
from eke.domain.identity import CelexIdentifier


def test_metadata_accepts_legal_references() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        legal_references=(
            EurLexLegalReference(
                kind=EurLexLegalReferenceKind.CITES,
                target_celex=CelexIdentifier.parse(
                    "32013R0575"
                ),
                source_predicate="work_cites_work",
            ),
        ),
    )

    assert len(metadata.legal_references) == 1


def test_metadata_rejects_invalid_reference_values() -> None:
    with pytest.raises(
        TypeError,
        match="legal_references",
    ):
        EurLexMetadata(
            celex_identifier=CelexIdentifier.parse(
                "32023R1114"
            ),
            legal_references=(
                "citation",  # type: ignore[arg-type]
            ),
        )
