"""Tests for explicit EUR-Lex temporal constraints."""

from datetime import date

import pytest

from eke.application.eurlex.temporal_constraints import (
    EurLexTemporalConstraint,
    EurLexTemporalConstraintKind,
    EurLexTemporalConstraints,
    EurLexTemporalRelation,
    EurLexTemporalUnit,
    normalize_temporal_constraints,
)


def _deadline(
    *,
    constraint_id: str = "constraint-1",
) -> EurLexTemporalConstraint:
    return EurLexTemporalConstraint(
        constraint_id=constraint_id,
        kind=EurLexTemporalConstraintKind.DEADLINE,
        relation=(
            EurLexTemporalRelation
            .NO_LATER_THAN
        ),
        text="no later than 15 March 2027",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The institution shall report no "
            "later than 15 March 2027."
        ),
        absolute_date=date(2027, 3, 15),
    )


def test_constraint_normalizes_values() -> None:
    constraint = EurLexTemporalConstraint(
        constraint_id=" constraint-1 ",
        kind=(
            EurLexTemporalConstraintKind
            .RELATIVE_OFFSET
        ),
        relation=EurLexTemporalRelation.WITHIN,
        text=" within   30 days ",
        source_rule_id=" rule-1 ",
        source_requirement_id=" requirement-1 ",
        source_node_id=" point-1 ",
        source_text=(
            "The institution shall report "
            "within 30 days."
        ),
        quantity=30,
        unit=EurLexTemporalUnit.DAY,
        anchor_text=" notification ",
        source_qualifier_id=" qualifier-1 ",
    )

    assert constraint.constraint_id == "constraint-1"
    assert constraint.text == "within 30 days"
    assert constraint.source_rule_id == "rule-1"
    assert constraint.source_requirement_id == (
        "requirement-1"
    )
    assert constraint.source_node_id == "point-1"
    assert constraint.anchor_text == "notification"
    assert constraint.source_qualifier_id == (
        "qualifier-1"
    )


def test_rejects_boolean_quantity() -> None:
    with pytest.raises(
        TypeError,
        match="quantity must be an integer",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .RELATIVE_OFFSET
            ),
            relation=(
                EurLexTemporalRelation.WITHIN
            ),
            text="within one day",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "within one day."
            ),
            quantity=True,
            unit=EurLexTemporalUnit.DAY,
        )


def test_rejects_non_positive_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="strictly positive",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .RELATIVE_OFFSET
            ),
            relation=(
                EurLexTemporalRelation.WITHIN
            ),
            text="within 0 days",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "within 0 days."
            ),
            quantity=0,
            unit=EurLexTemporalUnit.DAY,
        )


def test_requires_unit_for_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="quantity requires unit",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .RELATIVE_OFFSET
            ),
            relation=(
                EurLexTemporalRelation.WITHIN
            ),
            text="within 30 days",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "within 30 days."
            ),
            quantity=30,
        )


def test_requires_quantity_for_unit() -> None:
    with pytest.raises(
        ValueError,
        match="unit requires quantity",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .RELATIVE_OFFSET
            ),
            relation=(
                EurLexTemporalRelation.WITHIN
            ),
            text="within 30 days",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "within 30 days."
            ),
            unit=EurLexTemporalUnit.DAY,
        )


def test_rejects_absolute_date_with_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="mutually exclusive",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .DEADLINE
            ),
            relation=(
                EurLexTemporalRelation
                .NO_LATER_THAN
            ),
            text="no later than 15 March 2027",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "no later than 15 March 2027."
            ),
            absolute_date=date(2027, 3, 15),
            quantity=30,
            unit=EurLexTemporalUnit.DAY,
        )


def test_every_requires_quantity_and_unit() -> None:
    with pytest.raises(
        ValueError,
        match="EVERY requires quantity and unit",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .FREQUENCY
            ),
            relation=EurLexTemporalRelation.EVERY,
            text="every six months",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "every six months."
            ),
        )


def test_lexical_frequency_rejects_quantity() -> None:
    with pytest.raises(
        ValueError,
        match="must not define quantity",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .FREQUENCY
            ),
            relation=(
                EurLexTemporalRelation.ANNUALLY
            ),
            text="annually",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall report "
                "annually."
            ),
            quantity=1,
            unit=EurLexTemporalUnit.YEAR,
        )


def test_duration_requires_for_relation() -> None:
    with pytest.raises(
        ValueError,
        match="duration constraints require FOR",
    ):
        EurLexTemporalConstraint(
            constraint_id="constraint-1",
            kind=(
                EurLexTemporalConstraintKind
                .DURATION
            ),
            relation=(
                EurLexTemporalRelation.WITHIN
            ),
            text="within five years",
            source_rule_id="rule-1",
            source_requirement_id="requirement-1",
            source_node_id="point-1",
            source_text=(
                "The institution shall retain "
                "records within five years."
            ),
            quantity=5,
            unit=EurLexTemporalUnit.YEAR,
        )


def test_container_queries_constraints() -> None:
    deadline = _deadline()
    duration = EurLexTemporalConstraint(
        constraint_id="constraint-2",
        kind=EurLexTemporalConstraintKind.DURATION,
        relation=EurLexTemporalRelation.FOR,
        text="for five years",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The institution shall retain records "
            "for five years."
        ),
        quantity=5,
        unit=EurLexTemporalUnit.YEAR,
        source_qualifier_id="qualifier-1",
    )
    constraints = EurLexTemporalConstraints(
        constraints=(
            deadline,
            duration,
        )
    )

    assert constraints.constraint_by_id(
        "constraint-1"
    ) == deadline
    assert constraints.constraints_for_rule(
        "rule-1"
    ) == (
        deadline,
        duration,
    )
    assert constraints.constraints_for_qualifier(
        "qualifier-1"
    ) == (duration,)
    assert constraints.constraints_by_kind(
        EurLexTemporalConstraintKind.DURATION
    ) == (duration,)
    assert constraints.deadlines() == (deadline,)


def test_rejects_duplicate_constraint_ids() -> None:
    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        EurLexTemporalConstraints(
            constraints=(
                _deadline(),
                _deadline(),
            )
        )


def test_normalize_deduplicates_in_source_order() -> None:
    first = _deadline()
    second = EurLexTemporalConstraint(
        constraint_id="constraint-2",
        kind=EurLexTemporalConstraintKind.FREQUENCY,
        relation=EurLexTemporalRelation.MONTHLY,
        text="monthly",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "The institution shall report monthly."
        ),
    )

    normalized = normalize_temporal_constraints(
        (
            first,
            first,
            second,
        )
    )

    assert normalized.constraints == (
        first,
        second,
    )
