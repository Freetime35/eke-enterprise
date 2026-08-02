"""Tests for EUR-Lex corrigendum values."""

from datetime import date

from eke.application.eurlex import (
    EurLexCorrigendum,
    EurLexCorrigendumIdentifier,
    normalize_corrigenda,
)


def test_corrigendum_exposes_corrected_act() -> None:
    corrigendum = EurLexCorrigendum(
        identifier=EurLexCorrigendumIdentifier.parse(
            "32013L0036R(01)"
        ),
        publication_date=date(2014, 1, 10),
        source_predicate="work_has_corrigendum",
    )

    assert corrigendum.corrected_act.value == (
        "32013L0036"
    )


def test_normalizes_corrigenda_by_sequence() -> None:
    second = EurLexCorrigendum(
        identifier=EurLexCorrigendumIdentifier.parse(
            "32013L0036R(02)"
        ),
        source_predicate="work_has_corrigendum",
    )
    first = EurLexCorrigendum(
        identifier=EurLexCorrigendumIdentifier.parse(
            "32013L0036R(01)"
        ),
        source_predicate="work_has_corrigendum",
    )

    assert normalize_corrigenda(
        (second, first, first)
    ) == (
        first,
        second,
    )
