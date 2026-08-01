"""Validity period value object.

This module defines an immutable temporal interval used by the
EKE Enterprise canonical domain model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ValidityPeriod:
    """Represent an immutable inclusive validity period.

    Either boundary may be open. When both boundaries are provided,
    ``valid_from`` must not be later than ``valid_to``.

    Attributes:
        valid_from: Inclusive start date, or None for an open start.
        valid_to: Inclusive end date, or None for an open end.
    """

    valid_from: date | None = None
    valid_to: date | None = None

    def __post_init__(self) -> None:
        """Validate temporal invariants."""
        if self.valid_from is not None and not isinstance(self.valid_from, date):
            raise TypeError("valid_from must be a date or None")

        if self.valid_to is not None and not isinstance(self.valid_to, date):
            raise TypeError("valid_to must be a date or None")

        if (
            self.valid_from is not None
            and self.valid_to is not None
            and self.valid_from > self.valid_to
        ):
            raise ValueError("valid_from must not be later than valid_to")

    @property
    def is_open_start(self) -> bool:
        """Return whether the period has no lower boundary."""
        return self.valid_from is None

    @property
    def is_open_end(self) -> bool:
        """Return whether the period has no upper boundary."""
        return self.valid_to is None

    @property
    def is_open(self) -> bool:
        """Return whether at least one boundary is open."""
        return self.is_open_start or self.is_open_end

    @property
    def is_bounded(self) -> bool:
        """Return whether both boundaries are defined."""
        return not self.is_open

    def contains(self, value: date) -> bool:
        """Return whether a date falls inside the inclusive period.

        Args:
            value: Date to evaluate.

        Returns:
            True when the date falls within the period.

        Raises:
            TypeError: If value is not a date.
        """
        if not isinstance(value, date):
            raise TypeError("value must be a date")

        if self.valid_from is not None and value < self.valid_from:
            return False

        if self.valid_to is not None and value > self.valid_to:
            return False

        return True

    def overlaps(self, other: ValidityPeriod) -> bool:
        """Return whether this period overlaps another period.

        Boundaries are inclusive, so periods touching at one date
        overlap.

        Args:
            other: Period to compare.

        Returns:
            True when the periods share at least one date.

        Raises:
            TypeError: If other is not a ValidityPeriod.
        """
        if not isinstance(other, ValidityPeriod):
            raise TypeError("other must be a ValidityPeriod")

        if (
            self.valid_to is not None
            and other.valid_from is not None
            and self.valid_to < other.valid_from
        ):
            return False

        if (
            other.valid_to is not None
            and self.valid_from is not None
            and other.valid_to < self.valid_from
        ):
            return False

        return True
