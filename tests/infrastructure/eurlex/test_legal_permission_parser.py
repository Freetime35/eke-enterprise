"""Tests for explicit English legal-permission extraction."""

from eke.application.eurlex import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
    EurLexLegalPermissionKind,
)
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    EurLexLegalPermissionParser,
)


def test_extracts_only_positive_explicit_permissions() -> None:
    structure = EurLexDocumentStructure(
        nodes=(
            EurLexDocumentNode(
                node_id="article-20",
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
                parent_id="article-20",
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
                    "Competent authorities may "
                    "exchange information."
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
                    "Applicants are entitled to "
                    "submit additional evidence."
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
                    "The authority is authorised to "
                    "request further information."
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
                    "Institutions may not disclose "
                    "confidential information."
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
                    "The applicant is not allowed to "
                    "alter the submitted records."
                ),
            ),
        )
    )

    permissions = (
        EurLexLegalPermissionParser()
        .parse(
            structure,
            language=LanguageCode("en"),
        )
    )

    assert len(permissions.permissions) == 3
    first = permissions.permissions[0]
    assert first.kind is (
        EurLexLegalPermissionKind.MAY
    )
    assert first.subject == (
        "Competent authorities"
    )
    assert first.action == (
        "exchange information."
    )
    assert first.article_node_id == (
        "article-20"
    )
    assert first.paragraph_node_id == (
        "paragraph-1"
    )

    assert permissions.permissions[1].kind is (
        EurLexLegalPermissionKind
        .ENTITLED_TO
    )
    assert permissions.permissions[2].kind is (
        EurLexLegalPermissionKind
        .AUTHORISED_TO
    )


def test_returns_empty_for_non_english_structure() -> None:
    structure = EurLexDocumentStructure(
        nodes=()
    )

    permissions = (
        EurLexLegalPermissionParser()
        .parse(
            structure,
            language=LanguageCode("fr"),
        )
    )

    assert permissions.permissions == ()
