"""Tests for EUR-Lex version lineage values."""

from datetime import date

import pytest

from eke.application.eurlex import (
    EurLexVersionIdentifier,
    EurLexVersionLineage,
    EurLexVersionLineageKind,
    normalize_version_lineage,
)
from eke.domain.identity import CelexIdentifier


def test_parses_consolidated_version_identifier() -> None:
    identifier = EurLexVersionIdentifier.parse(
        "02013R0575-20240101"
    )

    assert identifier.value == (
        "02013R0575-20240101"
    )
    assert identifier.consolidation_date == (
        date(2024, 1, 1)
    )


def test_consolidated_version_requires_base_act() -> None:
    with pytest.raises(
        ValueError,
        match="must identify its base act",
    ):
        EurLexVersionLineage(
            kind=(
                EurLexVersionLineageKind
                .CONSOLIDATED_VERSION
            ),
            version_identifier=(
                EurLexVersionIdentifier.parse(
                    "02013R0575-20240101"
                )
            ),
            consolidation_date=date(2024, 1, 1),
            source_predicate="consolidated_version",
        )


def test_normalizes_lineage_chronologically() -> None:
    base = CelexIdentifier.parse("32013R0575")
    older = EurLexVersionLineage(
        kind=(
            EurLexVersionLineageKind
            .CONSOLIDATED_VERSION
        ),
        version_identifier=(
            EurLexVersionIdentifier.parse(
                "02013R0575-20240101"
            )
        ),
        base_act=base,
        consolidation_date=date(2024, 1, 1),
        source_predicate="consolidated_version",
    )
    newer = EurLexVersionLineage(
        kind=(
            EurLexVersionLineageKind
            .CONSOLIDATED_VERSION
        ),
        version_identifier=(
            EurLexVersionIdentifier.parse(
                "02013R0575-20250101"
            )
        ),
        base_act=base,
        consolidation_date=date(2025, 1, 1),
        source_predicate="consolidated_version",
    )

    assert normalize_version_lineage(
        (newer, older, older)
    ) == (
        older,
        newer,
    )


def test_rejects_mismatched_consolidation_date() -> None:
    with pytest.raises(
        ValueError,
        match="must match",
    ):
        EurLexVersionLineage(
            kind=(
                EurLexVersionLineageKind
                .CONSOLIDATED_VERSION
            ),
            version_identifier=(
                EurLexVersionIdentifier.parse(
                    "02013R0575-20240101"
                )
            ),
            base_act=CelexIdentifier.parse(
                "32013R0575"
            ),
            consolidation_date=date(2024, 2, 1),
            source_predicate="consolidated_version",
        )
