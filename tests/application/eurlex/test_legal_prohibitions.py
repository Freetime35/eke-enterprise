"""Tests for explicit EUR-Lex legal prohibitions."""

import pytest

from eke.application.eurlex import (
    EurLexLegalProhibition,
    EurLexLegalProhibitionKind,
    EurLexLegalProhibitions,
    normalize_legal_prohibitions,
)
from eke.domain.localization import LanguageCode


def test_normalizes_explicit_prohibition() -> None:
    prohibition = EurLexLegalProhibition(
        subject=" credit   institutions ",
        action=" disclose   confidential data ",
        kind=(
            EurLexLegalProhibitionKind
            .SHALL_NOT
        ),
        source_node_id=" point-1 ",
        source_text=(
            "Credit institutions shall not "
            "disclose confidential data."
        ),
        language=LanguageCode("en"),
        article_node_id=" article-25 ",
        paragraph_node_id=" paragraph-1 ",
    )

    assert prohibition.subject == (
        "credit institutions"
    )
    assert prohibition.action == (
        "disclose confidential data"
    )
    assert prohibition.article_node_id == (
        "article-25"
    )


def test_rejects_non_english_prohibition() -> None:
    with pytest.raises(
        ValueError,
        match="must be English",
    ):
        EurLexLegalProhibition(
            subject="les établissements",
            action="divulguer les données",
            kind=(
                EurLexLegalProhibitionKind
                .SHALL_NOT
            ),
            source_node_id="point-1",
            source_text=(
                "Les établissements ne doivent "
                "pas divulguer les données."
            ),
            language=LanguageCode("fr"),
        )


def test_container_filters_subject_and_article() -> None:
    prohibition = EurLexLegalProhibition(
        subject="applicants",
        action="alter submitted records",
        kind=(
            EurLexLegalProhibitionKind
            .NOT_ALLOWED_TO
        ),
        source_node_id="point-2",
        source_text=(
            "Applicants are not allowed to alter "
            "submitted records."
        ),
        language=LanguageCode("en"),
        article_node_id="article-30",
    )
    prohibitions = EurLexLegalProhibitions(
        prohibitions=(prohibition,)
    )

    assert prohibitions.prohibitions_for_subject(
        "Applicants"
    ) == (prohibition,)
    assert prohibitions.prohibitions_for_article(
        "article-30"
    ) == (prohibition,)


def test_deduplicates_prohibitions_in_source_order() -> None:
    prohibition = EurLexLegalProhibition(
        subject="institutions",
        action="use confidential information",
        kind=(
            EurLexLegalProhibitionKind.MAY_NOT
        ),
        source_node_id="point-3",
        source_text=(
            "Institutions may not use "
            "confidential information."
        ),
        language=LanguageCode("en"),
    )

    normalized = normalize_legal_prohibitions(
        (prohibition, prohibition)
    )

    assert normalized.prohibitions == (
        prohibition,
    )
