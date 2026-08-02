"""Tests for EUR-Lex table values."""

import pytest

from eke.application.eurlex import (
    EurLexTable,
    EurLexTableCell,
)


def test_table_preserves_cell_spans() -> None:
    table = EurLexTable(
        content_id="table-1",
        parent_node_id="annex-1",
        position=0,
        source_element="TABLE",
        cells=(
            EurLexTableCell(
                row=0,
                column=0,
                text="Header",
                row_span=2,
                column_span=3,
                is_header=True,
            ),
        ),
    )

    assert table.cells[0].row_span == 2
    assert table.cells[0].column_span == 3
    assert table.cells[0].is_header


def test_rejects_non_positive_span() -> None:
    with pytest.raises(
        ValueError,
        match="strictly positive",
    ):
        EurLexTableCell(
            row=0,
            column=0,
            column_span=0,
        )
