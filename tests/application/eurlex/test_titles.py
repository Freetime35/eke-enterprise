"""Tests for typed EUR-Lex titles."""

import pytest

from eke.application.eurlex import (
    EurLexTitle,
    EurLexTitleKind,
    title_kind_from_predicate,
)
from eke.domain.localization import LanguageCode


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        (
            "work_title",
            EurLexTitleKind.OFFICIAL,
        ),
        (
            "short_title",
            EurLexTitleKind.SHORT,
        ),
        (
            "alternative_title",
            EurLexTitleKind.ALTERNATIVE,
        ),
    ],
)
def test_maps_title_predicates(
    predicate: str,
    expected: EurLexTitleKind,
) -> None:
    assert (
        title_kind_from_predicate(predicate)
        is expected
    )


def test_title_kind_defaults_to_unknown() -> None:
    title = EurLexTitle(
        LanguageCode("en"),
        "Markets in Crypto-assets",
    )

    assert title.kind is EurLexTitleKind.UNKNOWN


def test_title_rejects_invalid_kind() -> None:
    with pytest.raises(
        TypeError,
        match="kind must be",
    ):
        EurLexTitle(
            LanguageCode("en"),
            "Markets in Crypto-assets",
            kind="OFFICIAL",  # type: ignore[arg-type]
        )
