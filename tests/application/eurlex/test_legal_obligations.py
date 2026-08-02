"""Tests for explicit EUR-Lex legal obligations."""

import pytest

from eke.application.eurlex import (
    EurLexLegalObligation,
    EurLexLegalObligationKind,
    EurLexLegalObligations,
    normalize_legal_obligations,
)
from eke.domain.localization import LanguageCode


def test_normalizes_explicit_obligation() -> None:
    obligation = EurLexLegalObligation(
        subject=" credit   institutions ",
        action=" submit   annual reports ",
        kind=EurLexLegalObligationKind.SHALL,
        source_node_id=" point-1 ",
        source_text=(
            "Credit institutions shall submit "
            "annual reports."
        ),
        language=LanguageCode("en"),
        article_node_id=" article-10 ",
        paragraph_node_id=" paragraph-1 ",
    )

    assert obligation.subject == (
        "credit institutions"
    )
    assert obligation.action == (
        "submit annual reports"
    )
    assert obligation.article_node_id == (
        "article-10"
    )


def test_rejects_non_english_obligation() -> None:
    with pytest.raises(
        ValueError,
        match="must be English",
    ):
        EurLexLegalObligation(
            subject="les établissements",
            action="soumettent un rapport",
            kind=(
                EurLexLegalObligationKind.SHALL
            ),
            source_node_id="point-1",
            source_text=(
                "Les établissements soumettent "
                "un rapport."
            ),
            language=LanguageCode("fr"),
        )


def test_container_filters_subject_and_article() -> None:
    obligation = EurLexLegalObligation(
        subject="competent authorities",
        action="cooperate with each other",
        kind=EurLexLegalObligationKind.MUST,
        source_node_id="point-2",
        source_text=(
            "Competent authorities must "
            "cooperate with each other."
        ),
        language=LanguageCode("en"),
        article_node_id="article-20",
    )
    obligations = EurLexLegalObligations(
        obligations=(obligation,)
    )

    assert obligations.obligations_for_subject(
        "Competent Authorities"
    ) == (obligation,)
    assert obligations.obligations_for_article(
        "article-20"
    ) == (obligation,)


def test_deduplicates_obligations_in_source_order() -> None:
    obligation = EurLexLegalObligation(
        subject="institutions",
        action="retain records",
        kind=EurLexLegalObligationKind.SHALL,
        source_node_id="point-3",
        source_text=(
            "Institutions shall retain records."
        ),
        language=LanguageCode("en"),
    )

    normalized = normalize_legal_obligations(
        (obligation, obligation)
    )

    assert normalized.obligations == (
        obligation,
    )
