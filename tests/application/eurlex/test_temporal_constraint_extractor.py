"""Tests for explicit EUR-Lex temporal extraction."""

from datetime import date

import pytest

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
    EurLexRuleQualifiers,
)
from eke.application.eurlex.temporal_constraint_extractor import (
    EurLexTemporalConstraintExtractor,
)
from eke.application.eurlex.temporal_constraints import (
    EurLexTemporalConstraintKind,
    EurLexTemporalRelation,
    EurLexTemporalUnit,
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
        action="report",
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


def test_extracts_quantities_dates_anchors_and_frequencies() -> None:
    source_text = (
        "The institution shall submit the report "
        "within 30 days of notification, retain "
        "records for a period of five years, "
        "review them every six months, and file "
        "annually, no later than 15 March 2027."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    constraints = (
        EurLexTemporalConstraintExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(constraints.constraints) == 5

    relative_offset = constraints.constraints[0]
    assert relative_offset.kind is (
        EurLexTemporalConstraintKind
        .RELATIVE_OFFSET
    )
    assert relative_offset.relation is (
        EurLexTemporalRelation.WITHIN
    )
    assert relative_offset.quantity == 30
    assert relative_offset.unit is (
        EurLexTemporalUnit.DAY
    )
    assert relative_offset.anchor_text == (
        "notification"
    )

    duration = constraints.constraints[1]
    assert duration.kind is (
        EurLexTemporalConstraintKind.DURATION
    )
    assert duration.relation is (
        EurLexTemporalRelation.FOR
    )
    assert duration.quantity == 5
    assert duration.unit is (
        EurLexTemporalUnit.YEAR
    )

    frequency = constraints.constraints[2]
    assert frequency.kind is (
        EurLexTemporalConstraintKind.FREQUENCY
    )
    assert frequency.relation is (
        EurLexTemporalRelation.EVERY
    )
    assert frequency.quantity == 6
    assert frequency.unit is (
        EurLexTemporalUnit.MONTH
    )

    lexical_frequency = constraints.constraints[3]
    assert lexical_frequency.relation is (
        EurLexTemporalRelation.ANNUALLY
    )

    deadline = constraints.constraints[4]
    assert deadline.kind is (
        EurLexTemporalConstraintKind.DEADLINE
    )
    assert deadline.relation is (
        EurLexTemporalRelation
        .NO_LATER_THAN
    )
    assert deadline.absolute_date == date(
        2027,
        3,
        15,
    )


def test_extracts_iso_dates_and_anchored_relations() -> None:
    source_text = (
        "The procedure shall apply from "
        "2027-01-01 until 31 December 2029 "
        "and after the notification."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    constraints = (
        EurLexTemporalConstraintExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(constraints.constraints) == 3

    start = constraints.constraints[0]
    assert start.kind is (
        EurLexTemporalConstraintKind.START
    )
    assert start.relation is (
        EurLexTemporalRelation.FROM
    )
    assert start.absolute_date == date(
        2027,
        1,
        1,
    )

    end = constraints.constraints[1]
    assert end.kind is (
        EurLexTemporalConstraintKind.END
    )
    assert end.relation is (
        EurLexTemporalRelation.UNTIL
    )
    assert end.absolute_date == date(
        2029,
        12,
        31,
    )

    anchored = constraints.constraints[2]
    assert anchored.kind is (
        EurLexTemporalConstraintKind.START
    )
    assert anchored.relation is (
        EurLexTemporalRelation.AFTER
    )
    assert anchored.anchor_text == (
        "the notification"
    )


def test_prefers_qualifier_provenance_over_rule_duplicate() -> None:
    source_text = (
        "If the report is submitted within "
        "30 days of notification, the institution "
        "shall retain it."
    )
    rule = _rule(source_text=source_text)
    qualifier = _qualifier(
        text="the report is submitted within "
        "30 days of notification",
        source_text=source_text,
    )

    constraints = (
        EurLexTemporalConstraintExtractor()
        .extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )
    )

    assert len(constraints.constraints) == 1

    constraint = constraints.constraints[0]
    assert constraint.source_rule_id == "rule-1"
    assert constraint.source_qualifier_id == (
        "qualifier-1"
    )
    assert constraint.source_node_id == "point-1"
    assert constraint.quantity == 30
    assert constraint.unit is (
        EurLexTemporalUnit.DAY
    )


def test_preserves_distinct_rule_and_qualifier_matches() -> None:
    source_text = (
        "If the application is filed within "
        "30 days, the institution shall report "
        "annually."
    )
    rule = _rule(source_text=source_text)
    qualifier = _qualifier(
        text="the application is filed within "
        "30 days",
        source_text=source_text,
    )

    constraints = (
        EurLexTemporalConstraintExtractor()
        .extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )
    )

    assert len(constraints.constraints) == 2
    assert constraints.constraints[0].relation is (
        EurLexTemporalRelation.ANNUALLY
    )
    assert constraints.constraints[0].source_qualifier_id is None
    assert constraints.constraints[1].relation is (
        EurLexTemporalRelation.WITHIN
    )
    assert constraints.constraints[1].source_qualifier_id == (
        "qualifier-1"
    )


def test_parses_compound_number_words() -> None:
    source_text = (
        "The institution shall report within "
        "twenty-one days of receipt."
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(source_text=source_text),
        )
    )

    constraints = (
        EurLexTemporalConstraintExtractor()
        .extract(
            rules=rules,
            qualifiers=EurLexRuleQualifiers(),
        )
    )

    assert len(constraints.constraints) == 1
    assert constraints.constraints[0].quantity == 21
    assert constraints.constraints[0].unit is (
        EurLexTemporalUnit.DAY
    )
    assert constraints.constraints[0].anchor_text == (
        "receipt"
    )


def test_rejects_qualifier_for_missing_rule() -> None:
    qualifier = _qualifier(
        rule_id="missing-rule",
        text="within 30 days",
        source_text=(
            "If within 30 days, the institution "
            "shall report."
        ),
    )

    with pytest.raises(
        ValueError,
        match="existing rules",
    ):
        EurLexTemporalConstraintExtractor().extract(
            rules=EurLexComplianceRules(),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
        )


def test_rejects_qualifier_requirement_mismatch() -> None:
    rule = _rule(
        source_text=(
            "The institution shall report."
        )
    )
    qualifier = _qualifier(
        requirement_id="requirement-2",
        text="within 30 days",
        source_text=(
            "If within 30 days, the institution "
            "shall report."
        ),
    )

    with pytest.raises(
        ValueError,
        match="requirement must match",
    ):
        EurLexTemporalConstraintExtractor().extract(
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
                    "The institution shall report "
                    "monthly."
                )
            ),
        )
    )
    extractor = EurLexTemporalConstraintExtractor()

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
        first.constraints[0].constraint_id
        == second.constraints[0].constraint_id
    )
