"""Tests for EUR-Lex rule qualifiers."""

import pytest

from eke.application.eurlex import (
    EurLexRuleQualifier,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
    EurLexRuleQualifiers,
)


def test_qualifier_normalizes_values_and_links() -> None:
    qualifier = EurLexRuleQualifier(
        qualifier_id=" qualifier-1 ",
        kind=EurLexRuleQualifierKind.CONDITION,
        marker=EurLexRuleQualifierMarker.IF,
        text=" the   threshold is exceeded ",
        source_rule_id=" rule-1 ",
        source_requirement_id=(
            " requirement-1 "
        ),
        source_node_id=" point-1 ",
        source_text=(
            "If the threshold is exceeded, "
            "the institution shall notify."
        ),
        referenced_node_ids=(
            " article-12 ",
            "article-12",
        ),
    )

    assert qualifier.text == (
        "the threshold is exceeded"
    )
    assert qualifier.referenced_node_ids == (
        "article-12",
    )


def test_container_queries_conditions_and_exceptions() -> None:
    condition = EurLexRuleQualifier(
        qualifier_id="qualifier-1",
        kind=EurLexRuleQualifierKind.CONDITION,
        marker=EurLexRuleQualifierMarker.WHERE,
        text="Article 12 applies",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "Where Article 12 applies, "
            "the institution shall notify."
        ),
    )
    exception = EurLexRuleQualifier(
        qualifier_id="qualifier-2",
        kind=EurLexRuleQualifierKind.EXCEPTION,
        marker=EurLexRuleQualifierMarker.UNLESS,
        text="otherwise provided",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "Unless otherwise provided, "
            "the institution shall notify."
        ),
    )
    qualifiers = EurLexRuleQualifiers(
        qualifiers=(
            condition,
            exception,
        )
    )

    assert qualifiers.qualifier_by_id(
        "qualifier-1"
    ) == condition
    assert qualifiers.conditions_for_rule(
        "rule-1"
    ) == (condition,)
    assert qualifiers.exceptions_for_rule(
        "rule-1"
    ) == (exception,)
    assert qualifiers.qualifiers_by_kind(
        EurLexRuleQualifierKind.EXCEPTION
    ) == (exception,)


def test_rejects_duplicate_qualifier_identifiers() -> None:
    qualifier = EurLexRuleQualifier(
        qualifier_id="qualifier-1",
        kind=EurLexRuleQualifierKind.CONDITION,
        marker=EurLexRuleQualifierMarker.IF,
        text="the condition applies",
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "If the condition applies, "
            "the institution shall notify."
        ),
    )

    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        EurLexRuleQualifiers(
            qualifiers=(
                qualifier,
                qualifier,
            )
        )
