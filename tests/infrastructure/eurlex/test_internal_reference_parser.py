"""Tests for English internal-reference extraction and resolution."""

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
    EurLexInternalReferenceKind,
)
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    EurLexInternalReferenceParser,
)


def test_extracts_and_conservatively_resolves_references() -> None:
    structure = EurLexDocumentStructure(
        nodes=(
            EurLexDocumentNode(
                node_id="article-12",
                kind=(
                    EurLexDocumentNodeKind.ARTICLE
                ),
                source_element="ARTICLE",
                position=0,
                ordinal="Article 12",
            ),
            EurLexDocumentNode(
                node_id="article-20",
                kind=(
                    EurLexDocumentNodeKind.ARTICLE
                ),
                source_element="ARTICLE",
                position=1,
                ordinal="Article 20",
            ),
            EurLexDocumentNode(
                node_id="paragraph-1",
                kind=(
                    EurLexDocumentNodeKind.PARAGRAPH
                ),
                source_element="PARAGRAPH",
                position=2,
                parent_id="article-20",
                ordinal="1",
            ),
            EurLexDocumentNode(
                node_id="point-a",
                kind=EurLexDocumentNodeKind.POINT,
                source_element="POINT",
                position=3,
                parent_id="paragraph-1",
                ordinal="(a)",
                text=(
                    "Institutions shall comply with "
                    "Article 12(2), point (a), "
                    "Section 4 and Annex II."
                ),
            ),
            EurLexDocumentNode(
                node_id="section-4",
                kind=(
                    EurLexDocumentNodeKind.SECTION
                ),
                source_element="SECTION",
                position=4,
                ordinal="Section 4",
            ),
            EurLexDocumentNode(
                node_id="annex-1",
                kind=EurLexDocumentNodeKind.ANNEX,
                source_element="ANNEX",
                position=5,
                ordinal="Annex I",
            ),
            EurLexDocumentNode(
                node_id="point-b",
                kind=EurLexDocumentNodeKind.POINT,
                source_element="POINT",
                position=6,
                parent_id="paragraph-1",
                ordinal="(b)",
                text=(
                    "Articles 4 to 7 shall apply."
                ),
            ),
        )
    )

    references = (
        EurLexInternalReferenceParser()
        .parse(
            structure,
            language=LanguageCode("en"),
        )
    )

    assert len(references.references) == 5

    article = references.references[0]
    assert article.kind is (
        EurLexInternalReferenceKind.ARTICLE
    )
    assert article.reference_text == (
        "Article 12(2)"
    )
    assert article.target_node_id == (
        "article-12"
    )
    assert article.article_node_id == (
        "article-20"
    )
    assert article.paragraph_node_id == (
        "paragraph-1"
    )

    point = references.references[1]
    assert point.kind is (
        EurLexInternalReferenceKind.POINT
    )
    assert point.target_node_id == "point-a"

    section = references.references[2]
    assert section.target_node_id == "section-4"

    annex = references.references[3]
    assert annex.target_node_id is None

    reference_range = references.references[4]
    assert reference_range.reference_text == (
        "Articles 4 to 7"
    )
    assert reference_range.target_node_id is None


def test_returns_empty_for_non_english_structure() -> None:
    structure = EurLexDocumentStructure(
        nodes=()
    )

    references = (
        EurLexInternalReferenceParser()
        .parse(
            structure,
            language=LanguageCode("fr"),
        )
    )

    assert references.references == ()
