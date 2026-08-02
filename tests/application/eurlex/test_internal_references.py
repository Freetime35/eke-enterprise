"""Tests for explicit EUR-Lex internal references."""

import pytest

from eke.application.eurlex import (
    EurLexInternalReference,
    EurLexInternalReferenceKind,
    EurLexInternalReferences,
    normalize_internal_references,
)
from eke.domain.localization import LanguageCode


def test_normalizes_internal_reference() -> None:
    reference = EurLexInternalReference(
        kind=EurLexInternalReferenceKind.ARTICLE,
        source_node_id=" point-1 ",
        source_text=(
            "Institutions shall comply with "
            "Article 12."
        ),
        reference_text=" Article   12 ",
        target_ordinal=" 12 ",
        target_node_id=" article-12 ",
        article_node_id=" article-20 ",
        paragraph_node_id=" paragraph-1 ",
        language=LanguageCode("en"),
    )

    assert reference.reference_text == "Article 12"
    assert reference.target_node_id == "article-12"
    assert reference.is_resolved


def test_rejects_non_english_reference() -> None:
    with pytest.raises(
        ValueError,
        match="must be English",
    ):
        EurLexInternalReference(
            kind=(
                EurLexInternalReferenceKind.ARTICLE
            ),
            source_node_id="point-1",
            source_text="Voir l'article 12.",
            reference_text="article 12",
            target_ordinal="12",
            language=LanguageCode("fr"),
        )


def test_container_filters_and_reports_unresolved() -> None:
    resolved = EurLexInternalReference(
        kind=EurLexInternalReferenceKind.ARTICLE,
        source_node_id="point-1",
        source_text="See Article 12.",
        reference_text="Article 12",
        target_ordinal="12",
        target_node_id="article-12",
        article_node_id="article-20",
        language=LanguageCode("en"),
    )
    unresolved = EurLexInternalReference(
        kind=EurLexInternalReferenceKind.ANNEX,
        source_node_id="point-2",
        source_text="See Annex II.",
        reference_text="Annex II",
        target_ordinal="II",
        language=LanguageCode("en"),
    )
    references = EurLexInternalReferences(
        references=(
            resolved,
            unresolved,
        )
    )

    assert references.references_from_node(
        "point-1"
    ) == (resolved,)
    assert references.references_to_node(
        "article-12"
    ) == (resolved,)
    assert references.references_for_article(
        "article-20"
    ) == (resolved,)
    assert references.unresolved_references() == (
        unresolved,
    )


def test_deduplicates_references_in_source_order() -> None:
    reference = EurLexInternalReference(
        kind=EurLexInternalReferenceKind.SECTION,
        source_node_id="point-3",
        source_text="See Section 2.",
        reference_text="Section 2",
        target_ordinal="2",
        language=LanguageCode("en"),
    )

    normalized = normalize_internal_references(
        (reference, reference)
    )

    assert normalized.references == (
        reference,
    )
