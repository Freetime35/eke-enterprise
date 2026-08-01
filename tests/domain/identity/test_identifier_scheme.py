"""Tests for the IdentifierScheme enumeration."""

from __future__ import annotations

import pytest

from eke.domain.identity import IdentifierScheme


def test_supported_identifier_schemes_are_defined() -> None:
    assert tuple(IdentifierScheme) == (
        IdentifierScheme.CELEX,
        IdentifierScheme.ELI,
        IdentifierScheme.CELLAR,
        IdentifierScheme.ECLI,
        IdentifierScheme.EURLEX,
    )


@pytest.mark.parametrize(
    ("scheme", "expected"),
    [
        (IdentifierScheme.CELEX, "CELEX"),
        (IdentifierScheme.ELI, "ELI"),
        (IdentifierScheme.CELLAR, "CELLAR"),
        (IdentifierScheme.ECLI, "ECLI"),
        (IdentifierScheme.EURLEX, "EURLEX"),
    ],
)
def test_scheme_value_matches_serialized_representation(
    scheme: IdentifierScheme,
    expected: str,
) -> None:
    assert scheme.value == expected
    assert str(scheme) == expected


def test_scheme_can_be_created_from_valid_string() -> None:
    assert IdentifierScheme("CELEX") is IdentifierScheme.CELEX


def test_scheme_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        IdentifierScheme("UNKNOWN")


def test_scheme_behaves_like_string() -> None:
    assert IdentifierScheme.CELEX == "CELEX"
    assert IdentifierScheme.CELEX.lower() == "celex"


def test_scheme_members_are_unique() -> None:
    values = [scheme.value for scheme in IdentifierScheme]

    assert len(values) == len(set(values))
