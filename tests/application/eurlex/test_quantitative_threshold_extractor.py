"""Tests for explicit EUR-Lex quantitative threshold extraction."""

from decimal import Decimal

import pytest

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
)
from eke.application.eurlex.quantitative_threshold_extractor import (
    EurLexQuantitativeThresholdExtractor,
)
from eke.application.eurlex.quantitative_thresholds import (
    EurLexQuantitativeComparator,
    EurLexQuantitativeUnitKind,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
    EurLexRuleQualifiers,
)
from eke.domain.localization import LanguageCode


def _rule(
    *,
    rule_id: str = "rule-1",
    requirement_id: str = "requirement-1",
    source_node_id: str = "point-1",
    source_text: str,
) -> EurLexComplianceRule:
    return EurLexComplianceRule(
        rule_id=rule_id,
        kind=(
            EurLexComplianceRuleKind
            .REQUIREMENT
        ),
        subject="institution",
        action="apply the requirement",
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
        language=LanguageCode("en"),
    )


def _qualifier(
    *,
    qualifier_id: str = "qualifier-1",
    rule_id: str = "rule-1",
    requirement_id: str = "requirement-1",
    source_node_id: str = "point-1",
    text: str,
    source_text: str,
) -> EurLexRuleQualifier:
    return EurLexRuleQualifier(
        qualifier_id=qualifier_id,
        kind=EurLexRuleQualifierKind.CONDITION,
        marker=EurLexRuleQualifierMarker.IF,
        text=text,
        source_rule_id=rule_id,
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
    )


def test_extracts_comparators_and_unit_kinds() -> None:
    source_text = (
        "The requirement applies at least "
        "EUR 5 000 000, less than 50 employees, "
        "not exceeding 10 %, exactly 25 tonnes, "
        "and more than 100 kWh."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(thresholds.thresholds) == 5

    currency = thresholds.thresholds[0]
    assert currency.comparator is (
        EurLexQuantitativeComparator
        .GREATER_THAN_OR_EQUAL_TO
    )
    assert currency.value == Decimal("5000000")
    assert currency.unit_kind is (
        EurLexQuantitativeUnitKind.CURRENCY
    )
    assert currency.currency_code == "EUR"

    count = thresholds.thresholds[1]
    assert count.comparator is (
        EurLexQuantitativeComparator.LESS_THAN
    )
    assert count.value == Decimal("50")
    assert count.unit_kind is (
        EurLexQuantitativeUnitKind.COUNT
    )
    assert count.unit_text == "employees"

    percent = thresholds.thresholds[2]
    assert percent.comparator is (
        EurLexQuantitativeComparator
        .LESS_THAN_OR_EQUAL_TO
    )
    assert percent.value == Decimal("10")
    assert percent.unit_kind is (
        EurLexQuantitativeUnitKind.PERCENT
    )
    assert percent.unit_text == "%"

    mass = thresholds.thresholds[3]
    assert mass.comparator is (
        EurLexQuantitativeComparator.EQUAL_TO
    )
    assert mass.value == Decimal("25")
    assert mass.unit_kind is (
        EurLexQuantitativeUnitKind.MASS
    )

    energy = thresholds.thresholds[4]
    assert energy.comparator is (
        EurLexQuantitativeComparator.GREATER_THAN
    )
    assert energy.value == Decimal("100")
    assert energy.unit_kind is (
        EurLexQuantitativeUnitKind.ENERGY
    )


def test_extracts_between_and_from_to_ranges() -> None:
    source_text = (
        "The ratio shall be between 5 % and 10 %, "
        "and the workforce shall be from "
        "20 employees to 50 employees."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(thresholds.thresholds) == 2

    percent = thresholds.thresholds[0]
    assert percent.comparator is (
        EurLexQuantitativeComparator.BETWEEN
    )
    assert percent.value == Decimal("5")
    assert percent.upper_value == Decimal("10")
    assert percent.unit_kind is (
        EurLexQuantitativeUnitKind.PERCENT
    )

    count = thresholds.thresholds[1]
    assert count.comparator is (
        EurLexQuantitativeComparator.BETWEEN
    )
    assert count.value == Decimal("20")
    assert count.upper_value == Decimal("50")
    assert count.unit_text == "employees"
    assert count.unit_kind is (
        EurLexQuantitativeUnitKind.COUNT
    )


def test_applies_decimal_and_named_multipliers() -> None:
    source_text = (
        "The threshold shall be more than "
        "USD 2.5 million and at least "
        "EUR 1,5 billion."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(thresholds.thresholds) == 2

    first = thresholds.thresholds[0]
    assert first.value == Decimal("2500000.0")
    assert first.currency_code == "USD"

    second = thresholds.thresholds[1]
    assert second.value == Decimal("1500000000.0")
    assert second.currency_code == "EUR"


def test_parses_grouped_numeric_formats() -> None:
    source_text = (
        "The threshold shall be at least "
        "EUR 5 000 000 and less than "
        "USD 1,000,000."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(thresholds.thresholds) == 2
    assert thresholds.thresholds[0].value == (
        Decimal("5000000")
    )
    assert thresholds.thresholds[1].value == (
        Decimal("1000000")
    )


def test_classifies_area_volume_length_and_time() -> None:
    source_text = (
        "The installation shall exceed 500 m², "
        "contain at most 20 litres, extend more "
        "than 30 metres, and operate for fewer "
        "than 24 hours."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(thresholds.thresholds) == 4
    assert thresholds.thresholds[0].unit_kind is (
        EurLexQuantitativeUnitKind.AREA
    )
    assert thresholds.thresholds[1].unit_kind is (
        EurLexQuantitativeUnitKind.VOLUME
    )
    assert thresholds.thresholds[2].unit_kind is (
        EurLexQuantitativeUnitKind.LENGTH
    )
    assert thresholds.thresholds[3].unit_kind is (
        EurLexQuantitativeUnitKind.TIME
    )


def test_prefers_qualifier_provenance_over_rule_duplicate() -> None:
    source_text = (
        "If the undertaking has fewer than "
        "50 employees, it shall report."
    )
    rule = _rule(source_text=source_text)
    qualifier = _qualifier(
        text=(
            "the undertaking has fewer than "
            "50 employees"
        ),
        source_text=source_text,
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )
    )

    assert len(thresholds.thresholds) == 1

    threshold = thresholds.thresholds[0]
    assert threshold.source_rule_id == "rule-1"
    assert threshold.source_qualifier_id == (
        "qualifier-1"
    )
    assert threshold.source_node_id == "point-1"
    assert threshold.value == Decimal("50")


def test_preserves_distinct_rule_and_qualifier_matches() -> None:
    source_text = (
        "If the undertaking has fewer than "
        "50 employees, it shall maintain at least "
        "EUR 1 million."
    )
    rule = _rule(source_text=source_text)
    qualifier = _qualifier(
        text=(
            "the undertaking has fewer than "
            "50 employees"
        ),
        source_text=source_text,
    )

    thresholds = (
        EurLexQuantitativeThresholdExtractor()
        .extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )
    )

    assert len(thresholds.thresholds) == 2

    currency = thresholds.thresholds[0]
    assert currency.currency_code == "EUR"
    assert currency.source_qualifier_id is None

    count = thresholds.thresholds[1]
    assert count.unit_kind is (
        EurLexQuantitativeUnitKind.COUNT
    )
    assert count.source_qualifier_id == (
        "qualifier-1"
    )


def test_rejects_descending_range() -> None:
    source_text = (
        "The ratio shall be between "
        "10 % and 5 %."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    with pytest.raises(
        ValueError,
        match="upper threshold value",
    ):
        EurLexQuantitativeThresholdExtractor().extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )


def test_rejects_range_with_different_currency() -> None:
    source_text = (
        "The amount shall be between "
        "EUR 5 million and USD 10 million."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    with pytest.raises(
        ValueError,
        match="same currency",
    ):
        EurLexQuantitativeThresholdExtractor().extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )


def test_rejects_range_with_different_units() -> None:
    source_text = (
        "The value shall be between "
        "5 kg and 10 tonnes."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    with pytest.raises(
        ValueError,
        match="same unit",
    ):
        EurLexQuantitativeThresholdExtractor().extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )


def test_rejects_qualifier_for_missing_rule() -> None:
    qualifier = _qualifier(
        rule_id="missing-rule",
        text="fewer than 50 employees",
        source_text=(
            "If fewer than 50 employees, "
            "the undertaking shall report."
        ),
    )

    with pytest.raises(
        ValueError,
        match="existing rules",
    ):
        EurLexQuantitativeThresholdExtractor().extract(
            rules=EurLexComplianceRules(),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )


def test_rejects_qualifier_requirement_mismatch() -> None:
    rule = _rule(
        source_text=(
            "The undertaking shall report."
        )
    )
    qualifier = _qualifier(
        requirement_id="requirement-2",
        text="fewer than 50 employees",
        source_text=(
            "If fewer than 50 employees, "
            "the undertaking shall report."
        ),
    )

    with pytest.raises(
        ValueError,
        match="requirement must match",
    ):
        EurLexQuantitativeThresholdExtractor().extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )


def test_extractor_is_deterministic() -> None:
    rules = EurLexComplianceRules(
        rules=(
            _rule(
                source_text=(
                    "The undertaking shall maintain "
                    "at least EUR 1 million."
                )
            ),
        )
    )
    extractor = EurLexQuantitativeThresholdExtractor()

    first = extractor.extract(
        rules=rules,
        qualifiers=EurLexRuleQualifiers(),
    )
    second = extractor.extract(
        rules=rules,
        qualifiers=EurLexRuleQualifiers(),
    )

    assert first == second
    assert (
        first.thresholds[0].threshold_id
        == second.thresholds[0].threshold_id
    )
