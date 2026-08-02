"""Tests for EUR-Lex document structures."""

import pytest

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)


def test_returns_direct_children_in_source_order() -> None:
    chapter = EurLexDocumentNode(
        node_id="chapter-1",
        kind=EurLexDocumentNodeKind.CHAPTER,
        source_element="CHAPTER",
        position=0,
    )
    article = EurLexDocumentNode(
        node_id="article-1",
        kind=EurLexDocumentNodeKind.ARTICLE,
        source_element="ARTICLE",
        position=1,
        parent_id="chapter-1",
    )
    paragraph = EurLexDocumentNode(
        node_id="paragraph-1",
        kind=EurLexDocumentNodeKind.PARAGRAPH,
        source_element="PARAGRAPH",
        position=2,
        parent_id="article-1",
    )
    structure = EurLexDocumentStructure(
        nodes=(
            chapter,
            article,
            paragraph,
        )
    )

    assert structure.children_of(
        "chapter-1"
    ) == (article,)
    assert structure.node_by_id(
        "paragraph-1"
    ) == paragraph


def test_rejects_unknown_parent() -> None:
    with pytest.raises(
        ValueError,
        match="existing node",
    ):
        EurLexDocumentStructure(
            nodes=(
                EurLexDocumentNode(
                    node_id="article-1",
                    kind=(
                        EurLexDocumentNodeKind.ARTICLE
                    ),
                    source_element="ARTICLE",
                    position=0,
                    parent_id="chapter-missing",
                ),
            )
        )
