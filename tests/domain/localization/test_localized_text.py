"""Tests for the LocalizedText value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from eke.domain.localization import LanguageCode, LocalizedText


def test_create_localized_text() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Capital Requirements Regulation",
    )

    assert text.language == LanguageCode("en")
    assert text.value == "Capital Requirements Regulation"


def test_string_conversion_returns_text_value() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    assert str(text) == "Banking regulation"


def test_text_value_is_preserved_exactly() -> None:
    value = "  Official title with preserved spacing  "
    text = LocalizedText(
        language=LanguageCode("en"),
        value=value,
    )

    assert text.value == value


@pytest.mark.parametrize("value", ["", " ", "\t", "\n", " \t\n "])
def test_empty_or_whitespace_only_value_is_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="value must not be empty"):
        LocalizedText(
            language=LanguageCode("en"),
            value=value,
        )


def test_non_string_value_is_rejected() -> None:
    with pytest.raises(TypeError, match="value must be a string"):
        LocalizedText(
            language=LanguageCode("en"),
            value=123,  # type: ignore[arg-type]
        )


def test_non_language_code_is_rejected() -> None:
    with pytest.raises(TypeError, match="language must be a LanguageCode"):
        LocalizedText(
            language="en",  # type: ignore[arg-type]
            value="Banking regulation",
        )


def test_is_language_returns_true_for_matching_language() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    assert text.is_language(LanguageCode("EN"))


def test_is_language_returns_false_for_different_language() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    assert not text.is_language(LanguageCode("fr"))


def test_is_language_rejects_invalid_type() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    with pytest.raises(TypeError, match="language must be a LanguageCode"):
        text.is_language("en")  # type: ignore[arg-type]


def test_localized_text_is_immutable() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    with pytest.raises(FrozenInstanceError):
        text.value = "Updated text"  # type: ignore[misc]


def test_localized_text_is_hashable_and_comparable() -> None:
    first = LocalizedText(
        language=LanguageCode("EN"),
        value="Banking regulation",
    )
    second = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    assert first == second
    assert hash(first) == hash(second)
    assert {first, second} == {first}


def test_repr_is_unambiguous() -> None:
    text = LocalizedText(
        language=LanguageCode("en"),
        value="Banking regulation",
    )

    assert repr(text) == (
        "LocalizedText("
        "language=LanguageCode('en'), "
        "value='Banking regulation')"
    )
