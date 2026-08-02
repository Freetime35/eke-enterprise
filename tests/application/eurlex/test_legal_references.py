"""Tests for source-backed legal references."""

import pytest

from eke.application.eurlex import (
    EurLexLegalReference,
    EurLexLegalReferenceKind,
    legal_reference_kind_from_predicate,
    normalize_legal_references,
)
from eke.domain.identity import CelexIdentifier


def test_reference_requires_explicit_target() -> None:
    with pytest.raises(
        ValueError,
        match="target_celex or target_uri",
    ):
        EurLexLegalReference(
            kind=EurLexLegalReferenceKind.CITES,
            source_predicate="work_cites_work",
        )


def test_reference_normalizes_source_values() -> None:
    reference = EurLexLegalReference(
        kind=EurLexLegalReferenceKind.TREATY_BASIS,
        target_uri=(
            " http://data.europa.eu/eli/"
            "treaty/tfeu_2012/art_114/oj "
        ),
        article="  Article 114   TFEU ",
        source_predicate=" work_based_on_treaty ",
    )

    assert reference.article == "Article 114 TFEU"
    assert reference.source_predicate == (
        "work_based_on_treaty"
    )


def test_normalizes_duplicate_references() -> None:
    reference = EurLexLegalReference(
        kind=EurLexLegalReferenceKind.CITES,
        target_celex=CelexIdentifier.parse(
            "32013R0575"
        ),
        source_predicate="work_cites_work",
    )

    assert normalize_legal_references(
        (reference, reference)
    ) == (reference,)


def test_maps_reference_predicate() -> None:
    assert legal_reference_kind_from_predicate(
        "work_based_on_treaty"
    ) is EurLexLegalReferenceKind.TREATY_BASIS
