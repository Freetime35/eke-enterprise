"""Tests for complex EUR-Lex document content."""

import pytest

from eke.application.eurlex import (
    EurLexComplexDocumentContent,
    EurLexFormula,
    EurLexTable,
)


def test_finds_content_by_identifier() -> None:
    table = EurLexTable(
        content_id="table-1",
        parent_node_id="annex-1",
        position=0,
        source_element="TABLE",
    )
    content = EurLexComplexDocumentContent(
        tables=(table,),
    )

    assert content.content_by_id(
        "table-1"
    ) == table


def test_rejects_duplicate_content_identifiers() -> None:
    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        EurLexComplexDocumentContent(
            tables=(
                EurLexTable(
                    content_id="content-1",
                    parent_node_id="annex-1",
                    position=0,
                    source_element="TABLE",
                ),
            ),
            formulas=(
                EurLexFormula(
                    content_id="content-1",
                    parent_node_id="annex-1",
                    position=1,
                    source_element="FORMULA",
                    source_text="x = 1",
                ),
            ),
        )
