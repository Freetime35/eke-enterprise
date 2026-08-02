"""Tests for corrigenda on EUR-Lex metadata."""

import pytest

from eke.application.eurlex import (
    EurLexCorrigendum,
    EurLexCorrigendumIdentifier,
    EurLexMetadata,
)
from eke.domain.identity import CelexIdentifier


def test_metadata_accepts_corrigenda() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32013L0036"
        ),
        corrigenda=(
            EurLexCorrigendum(
                identifier=(
                    EurLexCorrigendumIdentifier.parse(
                        "32013L0036R(01)"
                    )
                ),
                source_predicate=(
                    "work_has_corrigendum"
                ),
            ),
        ),
    )

    assert len(metadata.corrigenda) == 1


def test_metadata_rejects_invalid_corrigenda() -> None:
    with pytest.raises(
        TypeError,
        match="corrigenda",
    ):
        EurLexMetadata(
            celex_identifier=CelexIdentifier.parse(
                "32013L0036"
            ),
            corrigenda=(
                "R(01)",  # type: ignore[arg-type]
            ),
        )
