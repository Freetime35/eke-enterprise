"""Tests for EUR-Lex formula values."""

import pytest

from eke.application.eurlex import (
    EurLexFormula,
)


def test_formula_preserves_mathml() -> None:
    formula = EurLexFormula(
        content_id="formula-1",
        parent_node_id="annex-1",
        position=0,
        source_element="MATH",
        mathml="<math><mi>x</mi></math>",
    )

    assert formula.mathml == (
        "<math><mi>x</mi></math>"
    )


def test_formula_requires_source_representation() -> None:
    with pytest.raises(
        ValueError,
        match="must preserve",
    ):
        EurLexFormula(
            content_id="formula-1",
            parent_node_id="annex-1",
            position=0,
            source_element="FORMULA",
        )
