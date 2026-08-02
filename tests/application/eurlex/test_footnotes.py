"""Tests for EUR-Lex footnote values."""

from eke.application.eurlex import (
    EurLexFootnote,
)


def test_footnote_deduplicates_references() -> None:
    footnote = EurLexFootnote(
        content_id="fn-1",
        parent_node_id="article-1",
        text="See Article 2.",
        position=0,
        source_element="FOOTNOTE",
        referenced_from=(
            "article-1",
            "article-1",
        ),
    )

    assert footnote.referenced_from == (
        "article-1",
    )
