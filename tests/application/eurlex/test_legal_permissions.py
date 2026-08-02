"""Tests for explicit EUR-Lex legal permissions."""

import pytest

from eke.application.eurlex import (
    EurLexLegalPermission,
    EurLexLegalPermissionKind,
    EurLexLegalPermissions,
    normalize_legal_permissions,
)
from eke.domain.localization import LanguageCode


def test_normalizes_explicit_permission() -> None:
    permission = EurLexLegalPermission(
        subject=" competent   authorities ",
        action=" exchange   information ",
        kind=EurLexLegalPermissionKind.MAY,
        source_node_id=" point-1 ",
        source_text=(
            "Competent authorities may exchange "
            "information."
        ),
        language=LanguageCode("en"),
        article_node_id=" article-20 ",
        paragraph_node_id=" paragraph-1 ",
    )

    assert permission.subject == (
        "competent authorities"
    )
    assert permission.action == (
        "exchange information"
    )
    assert permission.article_node_id == (
        "article-20"
    )


def test_rejects_non_english_permission() -> None:
    with pytest.raises(
        ValueError,
        match="must be English",
    ):
        EurLexLegalPermission(
            subject="les autorités",
            action="échanger des informations",
            kind=(
                EurLexLegalPermissionKind.MAY
            ),
            source_node_id="point-1",
            source_text=(
                "Les autorités peuvent échanger "
                "des informations."
            ),
            language=LanguageCode("fr"),
        )


def test_container_filters_subject_and_article() -> None:
    permission = EurLexLegalPermission(
        subject="applicants",
        action="submit additional evidence",
        kind=(
            EurLexLegalPermissionKind
            .ENTITLED_TO
        ),
        source_node_id="point-2",
        source_text=(
            "Applicants are entitled to submit "
            "additional evidence."
        ),
        language=LanguageCode("en"),
        article_node_id="article-12",
    )
    permissions = EurLexLegalPermissions(
        permissions=(permission,)
    )

    assert permissions.permissions_for_subject(
        "Applicants"
    ) == (permission,)
    assert permissions.permissions_for_article(
        "article-12"
    ) == (permission,)


def test_deduplicates_permissions_in_source_order() -> None:
    permission = EurLexLegalPermission(
        subject="institutions",
        action="use the simplified method",
        kind=EurLexLegalPermissionKind.MAY,
        source_node_id="point-3",
        source_text=(
            "Institutions may use the "
            "simplified method."
        ),
        language=LanguageCode("en"),
    )

    normalized = normalize_legal_permissions(
        (permission, permission)
    )

    assert normalized.permissions == (
        permission,
    )
