"""Tests for structured EUR-Lex Boolean expressions."""

import pytest

from eke.application.eurlex import (
    EurLexBooleanAtom,
    EurLexBooleanExpressionTree,
    EurLexBooleanOperation,
    EurLexBooleanOperator,
    EurLexStructuredRuleQualifier,
    EurLexStructuredRuleQualifiers,
)


def test_tree_is_closed_and_queryable() -> None:
    left = EurLexBooleanAtom(
        expression_id="atom-a",
        text="A",
        source_text="A",
    )
    right = EurLexBooleanAtom(
        expression_id="atom-b",
        text="B",
        source_text="B",
    )
    operation = EurLexBooleanOperation(
        expression_id="operation-1",
        operator=EurLexBooleanOperator.AND,
        operand_ids=("atom-a", "atom-b"),
        source_text="A and B",
    )
    tree = EurLexBooleanExpressionTree(
        qualifier_id="qualifier-1",
        root_expression_id="operation-1",
        atoms=(left, right),
        operations=(operation,),
    )
    structured = EurLexStructuredRuleQualifiers(
        qualifiers=(
            EurLexStructuredRuleQualifier(
                qualifier_id="qualifier-1",
                expression_tree=tree,
            ),
        )
    )

    assert tree.atom_by_id("atom-a") == left
    assert tree.operation_by_id(
        "operation-1"
    ) == operation
    assert structured.expression_for_qualifier(
        "qualifier-1"
    ) == tree


def test_rejects_missing_operand() -> None:
    operation = EurLexBooleanOperation(
        expression_id="operation-1",
        operator=EurLexBooleanOperator.NOT,
        operand_ids=("atom-missing",),
        source_text="not A",
    )

    with pytest.raises(
        ValueError,
        match="operands must exist",
    ):
        EurLexBooleanExpressionTree(
            qualifier_id="qualifier-1",
            root_expression_id="operation-1",
            operations=(operation,),
        )


def test_rejects_invalid_operator_arity() -> None:
    with pytest.raises(
        ValueError,
        match="exactly one operand",
    ):
        EurLexBooleanOperation(
            expression_id="operation-1",
            operator=EurLexBooleanOperator.NOT,
            operand_ids=("atom-a", "atom-b"),
            source_text="not A",
        )
