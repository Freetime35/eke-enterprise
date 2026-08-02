"""Explicit quantitative thresholds derived from EUR-Lex compliance rules."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string"
        )

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(
            f"{name} must not be empty"
        )

    return normalized


def _normalize_optional_text(
    value: str | None,
    *,
    name: str,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string or None"
        )

    normalized = " ".join(value.split())
    return normalized or None


class EurLexQuantitativeComparator(StrEnum):
    """Canonical quantitative comparators."""

    EQUAL_TO = "EQUAL_TO"
    NOT_EQUAL_TO = "NOT_EQUAL_TO"
    GREATER_THAN = "GREATER_THAN"
    GREATER_THAN_OR_EQUAL_TO = (
        "GREATER_THAN_OR_EQUAL_TO"
    )
    LESS_THAN = "LESS_THAN"
    LESS_THAN_OR_EQUAL_TO = (
        "LESS_THAN_OR_EQUAL_TO"
    )
    BETWEEN = "BETWEEN"


class EurLexQuantitativeUnitKind(StrEnum):
    """Canonical kinds of quantitative units."""

    CURRENCY = "CURRENCY"
    PERCENT = "PERCENT"
    COUNT = "COUNT"
    MASS = "MASS"
    LENGTH = "LENGTH"
    AREA = "AREA"
    VOLUME = "VOLUME"
    ENERGY = "ENERGY"
    TIME = "TIME"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class EurLexQuantitativeThreshold:
    """Represent one explicit source-backed threshold."""

    threshold_id: str
    comparator: EurLexQuantitativeComparator
    text: str
    source_rule_id: str
    source_requirement_id: str
    source_node_id: str
    source_text: str
    value: Decimal
    upper_value: Decimal | None = None
    unit_text: str | None = None
    unit_kind: EurLexQuantitativeUnitKind = (
        EurLexQuantitativeUnitKind.OTHER
    )
    currency_code: str | None = None
    source_qualifier_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "threshold_id",
            "text",
            "source_rule_id",
            "source_requirement_id",
            "source_node_id",
            "source_text",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        for name in (
            "unit_text",
            "source_qualifier_id",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if not isinstance(
            self.comparator,
            EurLexQuantitativeComparator,
        ):
            raise TypeError(
                "comparator must be an "
                "EurLexQuantitativeComparator"
            )

        if not isinstance(
            self.unit_kind,
            EurLexQuantitativeUnitKind,
        ):
            raise TypeError(
                "unit_kind must be an "
                "EurLexQuantitativeUnitKind"
            )

        if not isinstance(
            self.value,
            Decimal,
        ):
            raise TypeError(
                "value must be a Decimal"
            )

        if (
            self.upper_value is not None
            and not isinstance(
                self.upper_value,
                Decimal,
            )
        ):
            raise TypeError(
                "upper_value must be a Decimal "
                "or None"
            )

        if not self.value.is_finite():
            raise ValueError(
                "value must be finite"
            )

        if (
            self.upper_value is not None
            and not self.upper_value.is_finite()
        ):
            raise ValueError(
                "upper_value must be finite"
            )

        if self.value < Decimal("0"):
            raise ValueError(
                "value must not be negative"
            )

        if (
            self.upper_value is not None
            and self.upper_value < Decimal("0")
        ):
            raise ValueError(
                "upper_value must not be negative"
            )

        if (
            self.comparator
            is EurLexQuantitativeComparator.BETWEEN
        ):
            if self.upper_value is None:
                raise ValueError(
                    "BETWEEN requires upper_value"
                )
            if self.upper_value < self.value:
                raise ValueError(
                    "upper_value must be greater "
                    "than or equal to value"
                )
        elif self.upper_value is not None:
            raise ValueError(
                "upper_value is only valid with "
                "BETWEEN"
            )

        normalized_currency_code = (
            _normalize_currency_code(
                self.currency_code
            )
        )
        object.__setattr__(
            self,
            "currency_code",
            normalized_currency_code,
        )

        if (
            self.unit_kind
            is EurLexQuantitativeUnitKind.CURRENCY
            and normalized_currency_code is None
        ):
            raise ValueError(
                "currency thresholds require "
                "currency_code"
            )

        if (
            normalized_currency_code is not None
            and self.unit_kind
            is not EurLexQuantitativeUnitKind.CURRENCY
        ):
            raise ValueError(
                "currency_code requires CURRENCY "
                "unit_kind"
            )

        if (
            self.unit_kind
            is EurLexQuantitativeUnitKind.PERCENT
            and self.unit_text is None
        ):
            object.__setattr__(
                self,
                "unit_text",
                "%",
            )


@dataclass(frozen=True, slots=True)
class EurLexQuantitativeThresholds:
    """Contain explicit quantitative thresholds."""

    thresholds: tuple[
        EurLexQuantitativeThreshold,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.thresholds,
            tuple,
        ):
            raise TypeError(
                "thresholds must be a tuple"
            )

        if any(
            not isinstance(
                threshold,
                EurLexQuantitativeThreshold,
            )
            for threshold in self.thresholds
        ):
            raise TypeError(
                "thresholds must contain "
                "EurLexQuantitativeThreshold values"
            )

        threshold_ids = tuple(
            threshold.threshold_id
            for threshold in self.thresholds
        )
        if len(threshold_ids) != len(
            set(threshold_ids)
        ):
            raise ValueError(
                "threshold identifiers must be unique"
            )

    def threshold_by_id(
        self,
        threshold_id: str,
    ) -> EurLexQuantitativeThreshold | None:
        """Return one threshold by identifier."""
        normalized = _normalize_required_text(
            threshold_id,
            name="threshold_id",
        )

        return next(
            (
                threshold
                for threshold in self.thresholds
                if threshold.threshold_id
                == normalized
            ),
            None,
        )

    def thresholds_for_rule(
        self,
        source_rule_id: str,
    ) -> tuple[EurLexQuantitativeThreshold, ...]:
        """Return thresholds attached to one rule."""
        normalized = _normalize_required_text(
            source_rule_id,
            name="source_rule_id",
        )

        return tuple(
            threshold
            for threshold in self.thresholds
            if threshold.source_rule_id
            == normalized
        )

    def thresholds_for_qualifier(
        self,
        source_qualifier_id: str,
    ) -> tuple[EurLexQuantitativeThreshold, ...]:
        """Return thresholds attached to one qualifier."""
        normalized = _normalize_required_text(
            source_qualifier_id,
            name="source_qualifier_id",
        )

        return tuple(
            threshold
            for threshold in self.thresholds
            if threshold.source_qualifier_id
            == normalized
        )

    def thresholds_by_comparator(
        self,
        comparator: EurLexQuantitativeComparator,
    ) -> tuple[EurLexQuantitativeThreshold, ...]:
        """Return thresholds using one comparator."""
        if not isinstance(
            comparator,
            EurLexQuantitativeComparator,
        ):
            raise TypeError(
                "comparator must be an "
                "EurLexQuantitativeComparator"
            )

        return tuple(
            threshold
            for threshold in self.thresholds
            if threshold.comparator is comparator
        )

    def thresholds_by_unit_kind(
        self,
        unit_kind: EurLexQuantitativeUnitKind,
    ) -> tuple[EurLexQuantitativeThreshold, ...]:
        """Return thresholds using one unit kind."""
        if not isinstance(
            unit_kind,
            EurLexQuantitativeUnitKind,
        ):
            raise TypeError(
                "unit_kind must be an "
                "EurLexQuantitativeUnitKind"
            )

        return tuple(
            threshold
            for threshold in self.thresholds
            if threshold.unit_kind is unit_kind
        )

    def currency_thresholds(
        self,
        currency_code: str | None = None,
    ) -> tuple[EurLexQuantitativeThreshold, ...]:
        """Return currency thresholds, optionally filtered by code."""
        if currency_code is None:
            return self.thresholds_by_unit_kind(
                EurLexQuantitativeUnitKind.CURRENCY
            )

        normalized = _normalize_currency_code(
            currency_code
        )
        if normalized is None:
            raise ValueError(
                "currency_code must not be empty"
            )

        return tuple(
            threshold
            for threshold in self.thresholds
            if (
                threshold.unit_kind
                is EurLexQuantitativeUnitKind.CURRENCY
                and threshold.currency_code
                == normalized
            )
        )


def normalize_quantitative_thresholds(
    thresholds: tuple[
        EurLexQuantitativeThreshold,
        ...,
    ],
) -> EurLexQuantitativeThresholds:
    """Deduplicate thresholds while preserving source order."""
    if not isinstance(thresholds, tuple):
        raise TypeError(
            "thresholds must be a tuple"
        )

    if any(
        not isinstance(
            threshold,
            EurLexQuantitativeThreshold,
        )
        for threshold in thresholds
    ):
        raise TypeError(
            "thresholds must contain "
            "EurLexQuantitativeThreshold values"
        )

    return EurLexQuantitativeThresholds(
        thresholds=tuple(
            dict.fromkeys(thresholds)
        )
    )


def _normalize_currency_code(
    value: str | None,
) -> str | None:
    normalized = _normalize_optional_text(
        value,
        name="currency_code",
    )
    if normalized is None:
        return None

    upper = normalized.upper()
    if (
        len(upper) != 3
        or not upper.isalpha()
        or not upper.isascii()
    ):
        raise ValueError(
            "currency_code must be a "
            "three-letter ASCII code"
        )

    return upper
