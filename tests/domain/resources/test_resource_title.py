"""Tests for the ResourceTitle business concept."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.resources import ResourceTitle
from eke.domain.temporal import ValidityPeriod


@pytest.fixture
def english_text() -> LocalizedText:
    return LocalizedText(
        language=LanguageCode("en"),
        value="Capital Requirements Regulation",
    )


def test_create_resource_title(
    english_text: LocalizedText,
) -> None:
    validity = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 12, 31),
    )

    title = ResourceTitle(
        text=english_text,
        validity=validity,
    )

    assert title.text == english_text
    assert title.validity == validity


def test_default_validity_is_fully_open(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    assert title.validity == ValidityPeriod()
    assert title.is_open_ended


def test_language_property_delegates_to_localized_text(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    assert title.language == LanguageCode("en")


def test_value_property_delegates_to_localized_text(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    assert title.value == "Capital Requirements Regulation"


def test_is_valid_on_uses_inclusive_validity_period(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(
        text=english_text,
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    assert title.is_valid_on(date(2024, 1, 1))
    assert title.is_valid_on(date(2024, 6, 1))
    assert title.is_valid_on(date(2024, 12, 31))
    assert not title.is_valid_on(date(2023, 12, 31))
    assert not title.is_valid_on(date(2025, 1, 1))


def test_is_valid_on_rejects_invalid_type(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    with pytest.raises(TypeError, match="value must be a date"):
        title.is_valid_on("2024-01-01")  # type: ignore[arg-type]


def test_has_language_reports_matching_language(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    assert title.has_language(LanguageCode("EN"))
    assert not title.has_language(LanguageCode("fr"))


def test_has_language_rejects_invalid_type(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    with pytest.raises(
        TypeError,
        match="language must be a LanguageCode",
    ):
        title.has_language("en")  # type: ignore[arg-type]


def test_same_language_overlapping_titles_overlap() -> None:
    first = ResourceTitle(
        text=LocalizedText(LanguageCode("en"), "First title"),
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 6, 30),
        ),
    )
    second = ResourceTitle(
        text=LocalizedText(LanguageCode("en"), "Second title"),
        validity=ValidityPeriod(
            valid_from=date(2024, 6, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    assert first.overlaps(second)
    assert second.overlaps(first)


def test_same_language_separate_titles_do_not_overlap() -> None:
    first = ResourceTitle(
        text=LocalizedText(LanguageCode("en"), "First title"),
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 6, 30),
        ),
    )
    second = ResourceTitle(
        text=LocalizedText(LanguageCode("en"), "Second title"),
        validity=ValidityPeriod(
            valid_from=date(2024, 7, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    assert not first.overlaps(second)


def test_different_language_titles_do_not_overlap() -> None:
    first = ResourceTitle(
        text=LocalizedText(LanguageCode("en"), "English title"),
    )
    second = ResourceTitle(
        text=LocalizedText(LanguageCode("fr"), "Titre français"),
    )

    assert not first.overlaps(second)


def test_overlaps_rejects_invalid_type(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    with pytest.raises(
        TypeError,
        match="other must be a ResourceTitle",
    ):
        title.overlaps("invalid")  # type: ignore[arg-type]


def test_invalid_text_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="text must be a LocalizedText",
    ):
        ResourceTitle(
            text="Title",  # type: ignore[arg-type]
        )


def test_invalid_validity_type_is_rejected(
    english_text: LocalizedText,
) -> None:
    with pytest.raises(
        TypeError,
        match="validity must be a ValidityPeriod",
    ):
        ResourceTitle(
            text=english_text,
            validity="always",  # type: ignore[arg-type]
        )


def test_resource_title_is_immutable(
    english_text: LocalizedText,
) -> None:
    title = ResourceTitle(text=english_text)

    with pytest.raises(FrozenInstanceError):
        title.validity = ValidityPeriod(  # type: ignore[misc]
            valid_from=date(2024, 1, 1)
        )


def test_resource_title_is_hashable_and_comparable(
    english_text: LocalizedText,
) -> None:
    first = ResourceTitle(text=english_text)
    second = ResourceTitle(text=english_text)

    assert first == second
    assert hash(first) == hash(second)
    assert {first, second} == {first}
