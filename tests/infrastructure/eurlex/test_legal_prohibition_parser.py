"""Tests for explicit English legal-prohibition extraction."""

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
    EurLexLegalProhibitionKind,
)
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    EurLexLegalProhibitionParser,
)


def test_extracts_only_explicit_prohibitions() -> None:
    structure = EurLexDocumentStructure(
        nodes=(
            EurLexDocumentNode(
                node_id="article-25",
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
                parent_id="article-25",
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
                    "Credit institutions shall not "
                    "disclose confidential data."
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
                    "Competent authorities must not "
                    "grant approval."
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
                    "Institutions may not use "
                    "confidential information."
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
                    "Applicants are prohibited from "
                    "altering submitted records."
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
                    "The authority is not authorised "
                    "to disclose the report."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-6",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=7,
                parent_id="paragraph-1",
                text=(
                    "The applicant is not allowed to "
                    "alter the submitted records."
                ),
            ),
            EurLexDocumentNode(
                node_id="point-7",
                kind=(
                    EurLexDocumentNodeKind.POINT
                ),
                source_element="POINT",
                position=8,
                parent_id="paragraph-1",
                text=(
                    "Competent authorities may "
                    "exchange information."
                ),
            ),
        )
    )

    prohibitions = (
        EurLexLegalProhibitionParser()
        .parse(
            structure,
            language=LanguageCode("en"),
        )
    )

    assert len(prohibitions.prohibitions) == 6
    assert prohibitions.prohibitions[0].kind is (
        EurLexLegalProhibitionKind.SHALL_NOT
    )
    assert prohibitions.prohibitions[1].kind is (
        EurLexLegalProhibitionKind.MUST_NOT
    )
    assert prohibitions.prohibitions[2].kind is (
        EurLexLegalProhibitionKind.MAY_NOT
    )
    assert prohibitions.prohibitions[3].kind is (
        EurLexLegalProhibitionKind
        .PROHIBITED_FROM
    )
    assert prohibitions.prohibitions[4].kind is (
        EurLexLegalProhibitionKind
        .NOT_AUTHORISED_TO
    )
    assert prohibitions.prohibitions[5].kind is (
        EurLexLegalProhibitionKind
        .NOT_ALLOWED_TO
    )

    first = prohibitions.prohibitions[0]
    assert first.article_node_id == (
        "article-25"
    )
    assert first.paragraph_node_id == (
        "paragraph-1"
    )


def test_returns_empty_for_non_english_structure() -> None:
    structure = EurLexDocumentStructure(
        nodes=()
    )

    prohibitions = (
        EurLexLegalProhibitionParser()
        .parse(
            structure,
            language=LanguageCode("fr"),
        )
    )

    assert prohibitions.prohibitions == ()
