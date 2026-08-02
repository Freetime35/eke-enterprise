"""Tests for version lineage on EUR-Lex metadata."""

import pytest

from eke.application.eurlex import (
    EurLexMetadata,
    EurLexVersionLineage,
    EurLexVersionLineageKind,
)
from eke.domain.identity import CelexIdentifier


def test_metadata_accepts_version_lineage() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32013R0575"
        ),
        version_lineage=(
            EurLexVersionLineage(
                kind=(
                    EurLexVersionLineageKind
                    .INITIAL_ACT
                ),
                act_celex=CelexIdentifier.parse(
                    "32013R0575"
                ),
                source_predicate="initial_act",
            ),
        ),
    )

    assert len(metadata.version_lineage) == 1


def test_metadata_rejects_invalid_lineage_values() -> None:
    with pytest.raises(
        TypeError,
        match="version_lineage",
    ):
        EurLexMetadata(
            celex_identifier=CelexIdentifier.parse(
                "32013R0575"
            ),
            version_lineage=(
                "version",  # type: ignore[arg-type]
            ),
        )
