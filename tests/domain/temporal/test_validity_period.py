"""Tests for the ValidityPeriod value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from eke.domain.temporal import ValidityPeriod


def test_create_bounded_validity_period() -> None:
    period = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 12, 31),
    )

    assert period.valid_from == date(2024, 1, 1)
    assert period.valid_to == date(2024, 12, 31)
    assert period.is_bounded
    assert not period.is_open


def test_create_fully_open_validity_period() -> None:
    period = ValidityPeriod()

    assert period.is_open
    assert period.is_open_start
    assert period.is_open_end
    assert not period.is_bounded


def test_create_open_start_period() -> None:
    period = ValidityPeriod(valid_to=date(2024, 12, 31))

    assert period.is_open_start
    assert not period.is_open_end


def test_create_open_end_period() -> None:
    period = ValidityPeriod(valid_from=date(2024, 1, 1))

    assert not period.is_open_start
    assert period.is_open_end


def test_equal_boundaries_are_allowed() -> None:
    boundary = date(2024, 1, 1)

    period = ValidityPeriod(
        valid_from=boundary,
        valid_to=boundary,
    )

    assert period.contains(boundary)


def test_reversed_boundaries_are_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="valid_from must not be later than valid_to",
    ):
        ValidityPeriod(
            valid_from=date(2024, 12, 31),
            valid_to=date(2024, 1, 1),
        )


def test_invalid_valid_from_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="valid_from must be a date or None",
    ):
        ValidityPeriod(
            valid_from="2024-01-01",  # type: ignore[arg-type]
        )


def test_invalid_valid_to_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="valid_to must be a date or None",
    ):
        ValidityPeriod(
            valid_to="2024-12-31",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2023, 12, 31), False),
        (date(2024, 1, 1), True),
        (date(2024, 6, 1), True),
        (date(2024, 12, 31), True),
        (date(2025, 1, 1), False),
    ],
)
def test_contains_uses_inclusive_boundaries(
    value: date,
    expected: bool,
) -> None:
    period = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 12, 31),
    )

    assert period.contains(value) is expected


def test_open_period_contains_any_date() -> None:
    period = ValidityPeriod()

    assert period.contains(date.min)
    assert period.contains(date.max)


def test_open_start_period_contains_earlier_dates() -> None:
    period = ValidityPeriod(valid_to=date(2024, 12, 31))

    assert period.contains(date(1900, 1, 1))
    assert not period.contains(date(2025, 1, 1))


def test_open_end_period_contains_later_dates() -> None:
    period = ValidityPeriod(valid_from=date(2024, 1, 1))

    assert not period.contains(date(2023, 12, 31))
    assert period.contains(date(2100, 1, 1))


def test_contains_rejects_invalid_type() -> None:
    period = ValidityPeriod()

    with pytest.raises(TypeError, match="value must be a date"):
        period.contains("2024-01-01")  # type: ignore[arg-type]


def test_overlapping_bounded_periods_are_detected() -> None:
    first = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 6, 30),
    )
    second = ValidityPeriod(
        valid_from=date(2024, 6, 1),
        valid_to=date(2024, 12, 31),
    )

    assert first.overlaps(second)
    assert second.overlaps(first)


def test_touching_periods_overlap() -> None:
    first = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 6, 30),
    )
    second = ValidityPeriod(
        valid_from=date(2024, 6, 30),
        valid_to=date(2024, 12, 31),
    )

    assert first.overlaps(second)


def test_separate_periods_do_not_overlap() -> None:
    first = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 6, 30),
    )
    second = ValidityPeriod(
        valid_from=date(2024, 7, 1),
        valid_to=date(2024, 12, 31),
    )

    assert not first.overlaps(second)
    assert not second.overlaps(first)


def test_open_period_overlaps_bounded_period() -> None:
    assert ValidityPeriod().overlaps(
        ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        )
    )


def test_open_end_and_open_start_periods_overlap() -> None:
    first = ValidityPeriod(valid_from=date(2024, 1, 1))
    second = ValidityPeriod(valid_to=date(2024, 6, 30))

    assert first.overlaps(second)


def test_overlaps_rejects_invalid_type() -> None:
    period = ValidityPeriod()

    with pytest.raises(
        TypeError,
        match="other must be a ValidityPeriod",
    ):
        period.overlaps("invalid")  # type: ignore[arg-type]


def test_validity_period_is_immutable() -> None:
    period = ValidityPeriod(valid_from=date(2024, 1, 1))

    with pytest.raises(FrozenInstanceError):
        period.valid_to = date(2024, 12, 31)  # type: ignore[misc]


def test_validity_period_is_hashable_and_comparable() -> None:
    first = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 12, 31),
    )
    second = ValidityPeriod(
        valid_from=date(2024, 1, 1),
        valid_to=date(2024, 12, 31),
    )

    assert first == second
    assert hash(first) == hash(second)
    assert {first, second} == {first}
