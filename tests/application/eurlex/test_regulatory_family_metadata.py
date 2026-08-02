"""Tests for regulatory families on EUR-Lex metadata."""

import pytest

from eke.application.eurlex import (
    EurLexMetadata,
    EurLexRegulatoryFamily,
    EurLexRegulatoryFamilyMatch,
    RegulatoryFamilyEvidenceKind,
)
from eke.domain.identity import CelexIdentifier


def test_metadata_accepts_family_matches() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        regulatory_families=(
            EurLexRegulatoryFamilyMatch(
                family=(
                    EurLexRegulatoryFamily.MICA
                ),
                matched_value="32023R1114",
                evidence_kind=(
                    RegulatoryFamilyEvidenceKind.CELEX
                ),
            ),
        ),
    )

    assert (
        metadata.regulatory_families[0].family
        is EurLexRegulatoryFamily.MICA
    )


def test_metadata_rejects_invalid_matches() -> None:
    with pytest.raises(
        TypeError,
        match="regulatory_families",
    ):
        EurLexMetadata(
            celex_identifier=CelexIdentifier.parse(
                "32023R1114"
            ),
            regulatory_families=(
                "MICA",  # type: ignore[arg-type]
            ),
        )
