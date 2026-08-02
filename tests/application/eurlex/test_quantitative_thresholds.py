"""Tests for explicit EUR-Lex quantitative thresholds."""

from decimal import Decimal

import pytest

from eke.application.eurlex.quantitative_thresholds import (
    EurLexQuantitativeComparator,
    EurLexQuantitativeThreshold,
    EurLexQuantitativeThresholds,
    EurLexQuantitativeUnitKind,
    normalize_quantitative_thresholds,
)


def _currency_threshold(
    *,
    threshold_id: str = "threshold-1",
) -> EurLexQuantitativeThreshold:
    return EurLexQuantitativeThreshold(
        threshold_id=threshold_id,
        comparator=(
            EurLexQuantitativeComparator
            .GREATER_THAN_OR_EQUAL_TO
        ),
        text="at least EUR 5 000 000",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The institution shall apply the "
            "requirement at least EUR 5 000 000."
        ),
        value=Decimal("5000000"),
        unit_text="EUR",
        unit_kind=(
            EurLexQuantitativeUnitKind.CURRENCY
        ),
        currency_code="EUR",
    )


def test_threshold_normalizes_text_and_currency() -> None:
    threshold = EurLexQuantitativeThreshold(
        threshold_id=" threshold-1 ",
        comparator=(
            EurLexQuantitativeComparator
            .GREATER_THAN_OR_EQUAL_TO
        ),
        text=" at   least   EUR 5 000 000 ",
        source_rule_id=" rule-1 ",
        source_requirement_id=" requirement-1 ",
        source_node_id=" point-1 ",
        source_text=(
            "The institution shall apply the "
            "requirement at least EUR 5 000 000."
        ),
        value=Decimal("5000000"),
        unit_text=" EUR ",
        unit_kind=(
            EurLexQuantitativeUnitKind.CURRENCY
        ),
        currency_code=" eur ",
        source_qualifier_id=" qualifier-1 ",
    )

    assert threshold.threshold_id == "threshold-1"
    assert threshold.text == (
        "at least EUR 5 000 000"
    )
    assert threshold.source_rule_id == "rule-1"
    assert threshold.source_requirement_id == (
        "requirement-1"
    )
    assert threshold.source_node_id == "point-1"
    assert threshold.unit_text == "EUR"
    assert threshold.currency_code == "EUR"
    assert threshold.source_qualifier_id == (
        "qualifier-1"
    )


def test_rejects_non_decimal_value() -> None:
    with pytest.raises(
        TypeError,
        match="value must be a Decimal",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .GREATER_THAN
            ),
            text="more than 10 employees",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The undertaking has more than "
                "10 employees."
            ),
            value=10,  # type: ignore[arg-type]
            unit_text="employees",
            unit_kind=(
                EurLexQuantitativeUnitKind.COUNT
            ),
        )


def test_rejects_non_finite_value() -> None:
    with pytest.raises(
        ValueError,
        match="value must be finite",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .GREATER_THAN
            ),
            text="more than infinity",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text="More than infinity.",
            value=Decimal("Infinity"),
        )


def test_rejects_negative_value() -> None:
    with pytest.raises(
        ValueError,
        match="value must not be negative",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .LESS_THAN
            ),
            text="less than -1",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text="Less than -1.",
            value=Decimal("-1"),
        )


def test_between_requires_upper_value() -> None:
    with pytest.raises(
        ValueError,
        match="BETWEEN requires upper_value",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator.BETWEEN
            ),
            text="between 5 and 10 percent",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The ratio shall be between "
                "5 and 10 percent."
            ),
            value=Decimal("5"),
            unit_text="%",
            unit_kind=(
                EurLexQuantitativeUnitKind.PERCENT
            ),
        )


def test_between_rejects_descending_range() -> None:
    with pytest.raises(
        ValueError,
        match="greater than or equal",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator.BETWEEN
            ),
            text="between 10 and 5 percent",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The ratio shall be between "
                "10 and 5 percent."
            ),
            value=Decimal("10"),
            upper_value=Decimal("5"),
            unit_text="%",
            unit_kind=(
                EurLexQuantitativeUnitKind.PERCENT
            ),
        )


def test_non_between_rejects_upper_value() -> None:
    with pytest.raises(
        ValueError,
        match="only valid with BETWEEN",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .GREATER_THAN
            ),
            text="more than 5 percent",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The ratio shall be more than "
                "5 percent."
            ),
            value=Decimal("5"),
            upper_value=Decimal("10"),
            unit_text="%",
            unit_kind=(
                EurLexQuantitativeUnitKind.PERCENT
            ),
        )


def test_currency_kind_requires_currency_code() -> None:
    with pytest.raises(
        ValueError,
        match="require currency_code",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .GREATER_THAN
            ),
            text="more than EUR 1000",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The amount is more than EUR 1000."
            ),
            value=Decimal("1000"),
            unit_text="EUR",
            unit_kind=(
                EurLexQuantitativeUnitKind.CURRENCY
            ),
        )


def test_currency_code_requires_currency_kind() -> None:
    with pytest.raises(
        ValueError,
        match="requires CURRENCY",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .GREATER_THAN
            ),
            text="more than 1000 units",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The amount is more than 1000 units."
            ),
            value=Decimal("1000"),
            unit_text="units",
            unit_kind=(
                EurLexQuantitativeUnitKind.COUNT
            ),
            currency_code="EUR",
        )


def test_rejects_invalid_currency_code() -> None:
    with pytest.raises(
        ValueError,
        match="three-letter ASCII code",
    ):
        EurLexQuantitativeThreshold(
            threshold_id="threshold-1",
            comparator=(
                EurLexQuantitativeComparator
                .GREATER_THAN
            ),
            text="more than EU 1000",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The amount is more than EU 1000."
            ),
            value=Decimal("1000"),
            unit_text="EU",
            unit_kind=(
                EurLexQuantitativeUnitKind.CURRENCY
            ),
            currency_code="EU",
        )


def test_percent_defaults_unit_text() -> None:
    threshold = EurLexQuantitativeThreshold(
        threshold_id="threshold-1",
        comparator=(
            EurLexQuantitativeComparator
            .LESS_THAN_OR_EQUAL_TO
        ),
        text="at most 10 percent",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The ratio shall be at most 10 percent."
        ),
        value=Decimal("10"),
        unit_kind=(
            EurLexQuantitativeUnitKind.PERCENT
        ),
    )

    assert threshold.unit_text == "%"


def test_container_queries_thresholds() -> None:
    currency = _currency_threshold()
    percent = EurLexQuantitativeThreshold(
        threshold_id="threshold-2",
        comparator=(
            EurLexQuantitativeComparator.BETWEEN
        ),
        text="between 5 and 10 percent",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The ratio shall be between "
            "5 and 10 percent."
        ),
        value=Decimal("5"),
        upper_value=Decimal("10"),
        unit_text="%",
        unit_kind=(
            EurLexQuantitativeUnitKind.PERCENT
        ),
        source_qualifier_id="qualifier-1",
    )
    thresholds = EurLexQuantitativeThresholds(
        thresholds=(
            currency,
            percent,
        )
    )

    assert thresholds.threshold_by_id(
        "threshold-1"
    ) == currency
    assert thresholds.thresholds_for_rule(
        "rule-1"
    ) == (
        currency,
        percent,
    )
    assert thresholds.thresholds_for_qualifier(
        "qualifier-1"
    ) == (percent,)
    assert thresholds.thresholds_by_comparator(
        EurLexQuantitativeComparator.BETWEEN
    ) == (percent,)
    assert thresholds.thresholds_by_unit_kind(
        EurLexQuantitativeUnitKind.PERCENT
    ) == (percent,)
    assert thresholds.currency_thresholds() == (
        currency,
    )
    assert thresholds.currency_thresholds(
        "eur"
    ) == (currency,)


def test_rejects_duplicate_threshold_ids() -> None:
    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        EurLexQuantitativeThresholds(
            thresholds=(
                _currency_threshold(),
                _currency_threshold(),
            )
        )


def test_normalize_deduplicates_in_source_order() -> None:
    first = _currency_threshold()
    second = EurLexQuantitativeThreshold(
        threshold_id="threshold-2",
        comparator=(
            EurLexQuantitativeComparator
            .LESS_THAN
        ),
        text="less than 50 employees",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The undertaking has less than "
            "50 employees."
        ),
        value=Decimal("50"),
        unit_text="employees",
        unit_kind=(
            EurLexQuantitativeUnitKind.COUNT
        ),
    )

    normalized = normalize_quantitative_thresholds(
        (
            first,
            first,
            second,
        )
    )

    assert normalized.thresholds == (
        first,
        second,
    )
