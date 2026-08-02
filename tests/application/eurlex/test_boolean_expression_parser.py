"""Tests for explicit Boolean qualifier parsing."""

import pytest

from eke.application.eurlex import (
    EurLexBooleanExpressionParseError,
    EurLexBooleanExpressionParser,
    EurLexBooleanOperator,
    EurLexRuleQualifier,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
)


def _qualifier(
    text: str,
) -> EurLexRuleQualifier:
    return EurLexRuleQualifier(
        qualifier_id="qualifier-1",
        kind=EurLexRuleQualifierKind.CONDITION,
        marker=EurLexRuleQualifierMarker.IF,
        text=text,
        source_rule_id="rule-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            f"If {text}, the institution "
            "shall notify."
        ),
    )


def test_respects_not_and_or_precedence() -> None:
    tree = EurLexBooleanExpressionParser().parse(
        _qualifier("A or B and not C")
    )

    root = tree.operation_by_id(
        tree.root_expression_id
    )
    assert root is not None
    assert root.operator is (
        EurLexBooleanOperator.OR
    )

    right = tree.operation_by_id(
        root.operand_ids[1]
    )
    assert right is not None
    assert right.operator is (
        EurLexBooleanOperator.AND
    )

    negation = tree.operation_by_id(
        right.operand_ids[1]
    )
    assert negation is not None
    assert negation.operator is (
        EurLexBooleanOperator.NOT
    )


def test_respects_nested_parentheses() -> None:
    tree = EurLexBooleanExpressionParser().parse(
        _qualifier(
            "A and (B or (C and D))"
        )
    )

    root = tree.operation_by_id(
        tree.root_expression_id
    )
    assert root is not None
    assert root.operator is (
        EurLexBooleanOperator.AND
    )

    nested_or = tree.operation_by_id(
        root.operand_ids[1]
    )
    assert nested_or is not None
    assert nested_or.operator is (
        EurLexBooleanOperator.OR
    )

    nested_and = tree.operation_by_id(
        nested_or.operand_ids[1]
    )
    assert nested_and is not None
    assert nested_and.operator is (
        EurLexBooleanOperator.AND
    )


def test_keeps_linguistic_negation_inside_atom() -> None:
    tree = EurLexBooleanExpressionParser().parse(
        _qualifier(
            "the applicant is not established "
            "in the Union and A"
        )
    )

    root = tree.operation_by_id(
        tree.root_expression_id
    )
    assert root is not None
    assert root.operator is (
        EurLexBooleanOperator.AND
    )
    assert tree.atoms[0].text == (
        "the applicant is not established "
        "in the Union"
    )


def test_parses_not_parenthesized_expression() -> None:
    tree = EurLexBooleanExpressionParser().parse(
        _qualifier("not (A or B)")
    )

    root = tree.operation_by_id(
        tree.root_expression_id
    )
    assert root is not None
    assert root.operator is (
        EurLexBooleanOperator.NOT
    )


def test_rejects_unbalanced_parentheses() -> None:
    with pytest.raises(
        EurLexBooleanExpressionParseError,
        match="unbalanced parentheses",
    ):
        EurLexBooleanExpressionParser().parse(
            _qualifier("(A and B")
        )
