"""Tests for explicit EUR-Lex legal definitions."""

import pytest

from eke.application.eurlex import (
    EurLexLegalDefinition,
    EurLexLegalDefinitions,
    normalize_legal_definitions,
)
from eke.domain.localization import LanguageCode


def test_normalizes_explicit_definition() -> None:
    definition = EurLexLegalDefinition(
        term=" credit   institution ",
        definition=" an undertaking whose business is deposits ",
        source_node_id=" point-1 ",
        source_text=(
            '"credit institution" means an undertaking '
            "whose business is deposits"
        ),
        language=LanguageCode("en"),
        article_node_id=" article-4 ",
        paragraph_node_id=" paragraph-1 ",
    )

    assert definition.term == (
        "credit institution"
    )
    assert definition.article_node_id == (
        "article-4"
    )


def test_rejects_non_english_definition() -> None:
    with pytest.raises(
        ValueError,
        match="must be English",
    ):
        EurLexLegalDefinition(
            term="établissement de crédit",
            definition="une entreprise",
            source_node_id="point-1",
            source_text=(
                '"établissement de crédit" '
                "désigne une entreprise"
            ),
            language=LanguageCode("fr"),
        )


def test_container_looks_up_term_and_article() -> None:
    definition = EurLexLegalDefinition(
        term="competent authority",
        definition="a public authority",
        source_node_id="point-2",
        source_text=(
            '"competent authority" means '
            "a public authority"
        ),
        language=LanguageCode("en"),
        article_node_id="article-4",
    )
    definitions = EurLexLegalDefinitions(
        definitions=(definition,)
    )

    assert definitions.definition_by_term(
        "Competent Authority"
    ) == definition
    assert definitions.definitions_for_article(
        "article-4"
    ) == (definition,)


def test_deduplicates_definitions_in_source_order() -> None:
    definition = EurLexLegalDefinition(
        term="financial institution",
        definition="an undertaking other than a bank",
        source_node_id="point-3",
        source_text=(
            '"financial institution" means '
            "an undertaking other than a bank"
        ),
        language=LanguageCode("en"),
    )

    normalized = normalize_legal_definitions(
        (definition, definition)
    )

    assert normalized.definitions == (
        definition,
    )
