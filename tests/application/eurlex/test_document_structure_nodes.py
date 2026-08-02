"""Tests for EUR-Lex document structure nodes."""

import pytest

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
)


def test_normalizes_document_node_values() -> None:
    node = EurLexDocumentNode(
        node_id=" article-1 ",
        kind=EurLexDocumentNodeKind.ARTICLE,
        ordinal=" 1 ",
        heading=" Subject   matter ",
        text=" This Regulation   lays down rules. ",
        parent_id=" chapter-1 ",
        source_element=" ARTICLE ",
        position=4,
        embedded_content_ids=(
            "table-1",
            "table-1",
        ),
    )

    assert node.node_id == "article-1"
    assert node.heading == "Subject matter"
    assert node.text == (
        "This Regulation lays down rules."
    )
    assert node.embedded_content_ids == (
        "table-1",
    )


def test_rejects_self_parent() -> None:
    with pytest.raises(
        ValueError,
        match="own parent",
    ):
        EurLexDocumentNode(
            node_id="article-1",
            kind=EurLexDocumentNodeKind.ARTICLE,
            source_element="ARTICLE",
            position=0,
            parent_id="article-1",
        )
