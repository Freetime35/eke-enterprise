"""Tests for explicit English legal-definition extraction."""

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    EurLexLegalDefinitionParser,
)


def test_extracts_only_explicit_english_definitions() -> None:
    structure = EurLexDocumentStructure(
        nodes=(
            EurLexDocumentNode(
                node_id="article-4",
                kind=(
                    EurLexDocumentNodeKind.ARTICLE
                ),
                source_element="ARTICLE",
                position=0,
            ),
            EurLexDocumentNode(
                node_id="paragraph-1",
                kind=(
                    EurLexDocumentNodeKind.PARAGRAPH
                ),
                source_element="PARAGRAPH",
                position=1,
                parent_id="article-4",
            ),
            EurLexDocumentNode(
                node_id="point-1",
                kind=EurLexDocumentNodeKind.POINT,
                source_element="POINT",
                position=2,
                parent_id="paragraph-1",
                text=(
                    '"credit institution" means '
                    "an undertaking whose business "
                    "is to take deposits."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-2",
                kind=EurLexDocumentNodeKind.POINT,
                source_element="POINT",
                position=3,
                parent_id="paragraph-1",
                text=(
                    "Institutions shall report "
                    "the required information."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-3",
                kind=EurLexDocumentNodeKind.POINT,
                source_element="POINT",
                position=4,
                parent_id="paragraph-1",
                text=(
                    "'competent authority' shall mean "
                    "a public authority."
                ),
            ),
        )
    )

    definitions = (
        EurLexLegalDefinitionParser()
        .parse(
            structure,
            language=LanguageCode("en"),
        )
    )

    assert len(definitions.definitions) == 2
    first = definitions.definitions[0]
    assert first.term == "credit institution"
    assert first.article_node_id == "article-4"
    assert first.paragraph_node_id == (
        "paragraph-1"
    )
    assert definitions.definitions[1].term == (
        "competent authority"
    )


def test_returns_empty_for_non_english_structure() -> None:
    structure = EurLexDocumentStructure(
        nodes=()
    )

    definitions = (
        EurLexLegalDefinitionParser()
        .parse(
            structure,
            language=LanguageCode("fr"),
        )
    )

    assert definitions.definitions == ()
