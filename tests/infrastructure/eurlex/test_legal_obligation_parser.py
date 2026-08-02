"""Tests for explicit English legal-obligation extraction."""

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
    EurLexLegalObligationKind,
)
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    EurLexLegalObligationParser,
)


def test_extracts_only_positive_explicit_obligations() -> None:
    structure = EurLexDocumentStructure(
        nodes=(
            EurLexDocumentNode(
                node_id="article-10",
                kind=(
                    EurLexDocumentNodeKind.ARTICLE
                ),
                source_element="ARTICLE",
                position=0,
            ),
            EurLexDocumentNode(
                node_id="paragraph-1",
                kind=(
                    EurLexDocumentNodeKind
                    .PARAGRAPH
                ),
                source_element="PARAGRAPH",
                position=1,
                parent_id="article-10",
            ),
            EurLexDocumentNode(
                node_id="point-1",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=2,
                parent_id="paragraph-1",
                text=(
                    "Credit institutions shall "
                    "submit annual reports."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-2",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=3,
                parent_id="paragraph-1",
                text=(
                    "Competent authorities must "
                    "cooperate with each other."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-3",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=4,
                parent_id="paragraph-1",
                text=(
                    "Institutions shall not "
                    "disclose confidential data."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-4",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=5,
                parent_id="paragraph-1",
                text=(
                    '"credit institution" means '
                    "an undertaking."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-5",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=6,
                parent_id="paragraph-1",
                text=(
                    "The applicant is required to "
                    "provide supporting evidence."
                ),
            ),
        )
    )

    obligations = (
        EurLexLegalObligationParser()
        .parse(
            structure,
            language=LanguageCode("en"),
        )
    )

    assert len(obligations.obligations) == 3
    first = obligations.obligations[0]
    assert first.kind is (
        EurLexLegalObligationKind.SHALL
    )
    assert first.subject == (
        "Credit institutions"
    )
    assert first.action == (
        "submit annual reports."
    )
    assert first.article_node_id == (
        "article-10"
    )
    assert first.paragraph_node_id == (
        "paragraph-1"
    )

    assert obligations.obligations[1].kind is (
        EurLexLegalObligationKind.MUST
    )
    assert obligations.obligations[2].kind is (
        EurLexLegalObligationKind.REQUIRED_TO
    )


def test_returns_empty_for_non_english_structure() -> None:
    structure = EurLexDocumentStructure(
        nodes=()
    )

    obligations = (
        EurLexLegalObligationParser()
        .parse(
            structure,
            language=LanguageCode("fr"),
        )
    )

    assert obligations.obligations == ()
