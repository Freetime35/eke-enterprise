"""Tests for the ClassificationConcept value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from eke.domain.classification import (
    ClassificationConcept,
    ClassificationScheme,
)
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.temporal import ValidityPeriod


@pytest.fixture
def label() -> LocalizedText:
    return LocalizedText(
        LanguageCode("en"),
        "Banking supervision",
    )


def test_create_classification_concept(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        scheme=ClassificationScheme.EUROVOC,
        code="2406",
        label=label,
    )

    assert concept.scheme is ClassificationScheme.EUROVOC
    assert concept.code == "2406"
    assert concept.label == label
    assert concept.validity == ValidityPeriod()


def test_language_and_label_value_delegate_to_label(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    assert concept.language == LanguageCode("en")
    assert concept.label_value == "Banking supervision"


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        (
            "scheme",
            "EUROVOC",
            "scheme must be a ClassificationScheme",
        ),
        (
            "code",
            2406,
            "code must be a string",
        ),
        (
            "label",
            "Banking supervision",
            "label must be a LocalizedText",
        ),
        (
            "validity",
            "always",
            "validity must be a ValidityPeriod",
        ),
    ],
)
def test_invalid_field_types_are_rejected(
    label: LocalizedText,
    field_name: str,
    value: object,
    message: str,
) -> None:
    arguments: dict[str, object] = {
        "scheme": ClassificationScheme.EUROVOC,
        "code": "2406",
        "label": label,
        "validity": ValidityPeriod(),
    }
    arguments[field_name] = value

    with pytest.raises(TypeError, match=message):
        ClassificationConcept(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("code", ["", " ", "\t", "\n"])
def test_empty_code_is_rejected(
    label: LocalizedText,
    code: str,
) -> None:
    with pytest.raises(ValueError, match="code must not be empty"):
        ClassificationConcept(
            ClassificationScheme.EUROVOC,
            code,
            label,
        )


def test_code_is_preserved_exactly(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.INTERNAL,
        "  CODE-01  ",
        label,
    )

    assert concept.code == "  CODE-01  "


def test_has_code_reports_exact_code(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    assert concept.has_code("2406")
    assert not concept.has_code("02406")


def test_has_code_rejects_invalid_type(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    with pytest.raises(TypeError, match="code must be a string"):
        concept.has_code(2406)  # type: ignore[arg-type]


def test_belongs_to_scheme_reports_membership(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    assert concept.belongs_to_scheme(
        ClassificationScheme.EUROVOC
    )
    assert not concept.belongs_to_scheme(
        ClassificationScheme.POLICY_AREA
    )


def test_belongs_to_scheme_rejects_invalid_type(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    with pytest.raises(
        TypeError,
        match="scheme must be a ClassificationScheme",
    ):
        concept.belongs_to_scheme(  # type: ignore[arg-type]
            "EUROVOC"
        )


def test_has_language_reports_label_language(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    assert concept.has_language(LanguageCode("EN"))
    assert not concept.has_language(LanguageCode("fr"))


def test_is_valid_on_uses_validity_period(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
        ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    assert concept.is_valid_on(date(2024, 1, 1))
    assert concept.is_valid_on(date(2024, 12, 31))
    assert not concept.is_valid_on(date(2025, 1, 1))


def test_query_methods_delegate_type_validation(
    label: LocalizedText,
) -> None:
    concept = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    with pytest.raises(
        TypeError,
        match="language must be a LanguageCode",
    ):
        concept.has_language("en")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="value must be a date"):
        concept.is_valid_on("today")  # type: ignore[arg-type]


def test_concept_is_immutable_hashable_and_comparable(
    label: LocalizedText,
) -> None:
    first = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )
    second = ClassificationConcept(
        ClassificationScheme.EUROVOC,
        "2406",
        label,
    )

    assert first == second
    assert hash(first) == hash(second)

    with pytest.raises(FrozenInstanceError):
        first.code = "changed"  # type: ignore[misc]
