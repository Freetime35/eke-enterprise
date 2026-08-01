"""Tests for the LanguageCode value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from eke.domain.localization import LanguageCode


def test_create_language_code_from_lowercase_value() -> None:
    language = LanguageCode("en")

    assert language.value == "en"
    assert str(language) == "en"


def test_language_code_normalizes_uppercase_value() -> None:
    language = LanguageCode("EN")

    assert language.value == "en"
    assert language.to_uppercase() == "EN"


def test_language_code_trims_surrounding_whitespace() -> None:
    language = LanguageCode(" en ")

    assert language.value == "en"


def test_from_string_returns_language_code() -> None:
    language = LanguageCode.from_string("fr")

    assert language == LanguageCode("fr")


@pytest.mark.parametrize(
    "value",
    [
        "",
        "e",
        "eng",
        "1n",
        "e-",
        "éé",
        "english",
    ],
)
def test_invalid_language_code_is_rejected(value: str) -> None:
    with pytest.raises(
        ValueError,
        match="two-letter ASCII language code",
    ):
        LanguageCode(value)


def test_non_string_value_is_rejected() -> None:
    with pytest.raises(TypeError, match="value must be a string"):
        LanguageCode(123)  # type: ignore[arg-type]


def test_language_code_is_immutable() -> None:
    language = LanguageCode("en")

    with pytest.raises(FrozenInstanceError):
        language.value = "fr"  # type: ignore[misc]


def test_language_code_is_hashable_and_comparable() -> None:
    first = LanguageCode("EN")
    second = LanguageCode("en")

    assert first == second
    assert hash(first) == hash(second)
    assert {first, second} == {first}


def test_repr_is_unambiguous() -> None:
    language = LanguageCode("en")

    assert repr(language) == "LanguageCode('en')"
