"""Tests for EUR-Lex corrigendum identifiers."""

import pytest

from eke.application.eurlex import (
    EurLexCorrigendumIdentifier,
)
from eke.domain.identity import CelexIdentifier


def test_parses_corrigendum_identifier() -> None:
    identifier = EurLexCorrigendumIdentifier.parse(
        "32013L0036R(01)"
    )

    assert identifier.base_act == (
        CelexIdentifier.parse("32013L0036")
    )
    assert identifier.sequence == 1
    assert identifier.value == (
        "32013L0036R(01)"
    )


def test_normalizes_corrigendum_identifier() -> None:
    identifier = EurLexCorrigendumIdentifier.parse(
        " 32013l0036r(02) "
    )

    assert identifier.value == (
        "32013L0036R(02)"
    )


@pytest.mark.parametrize(
    "value",
    [
        "32013L0036",
        "32013L0036R(00)",
        "32013L0036R(1)",
        "02013L0036R(01)",
    ],
)
def test_rejects_invalid_corrigendum_identifier(
    value: str,
) -> None:
    with pytest.raises(ValueError):
        EurLexCorrigendumIdentifier.parse(value)
