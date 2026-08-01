"""Tests for the ClassificationScheme enumeration."""

from __future__ import annotations

import pytest

from eke.domain.classification import ClassificationScheme


@pytest.mark.parametrize(
    "scheme",
    list(ClassificationScheme),
)
def test_classification_scheme_serializes_to_stable_string(
    scheme: ClassificationScheme,
) -> None:
    assert str(scheme) == scheme.value


def test_classification_scheme_members_are_unique() -> None:
    values = [scheme.value for scheme in ClassificationScheme]

    assert len(values) == len(set(values))


def test_classification_scheme_can_be_created_from_valid_string() -> None:
    assert (
        ClassificationScheme("EUROVOC")
        is ClassificationScheme.EUROVOC
    )


def test_classification_scheme_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        ClassificationScheme("UNKNOWN")
