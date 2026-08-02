"""Tests for EUR-Lex visual elements."""

from eke.application.eurlex import (
    EurLexVisualElement,
    EurLexVisualKind,
)


def test_visual_preserves_source_metadata() -> None:
    visual = EurLexVisualElement(
        content_id="figure-1",
        parent_node_id="annex-1",
        kind=EurLexVisualKind.CHART,
        position=0,
        source_element="FIGURE",
        source_uri=" chart.svg ",
        media_type=" image/svg+xml ",
    )

    assert visual.source_uri == "chart.svg"
    assert visual.media_type == (
        "image/svg+xml"
    )
