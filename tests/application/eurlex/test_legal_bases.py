"""Tests for explicit EUR-Lex legal bases."""

import pytest

from eke.application.eurlex import (
    EurLexLegalBasis,
    EurLexLegalBasisKind,
    legal_basis_kind_from_predicate,
    normalize_legal_bases,
)
from eke.domain.identity import CelexIdentifier


def test_legal_basis_requires_explicit_target() -> None:
    with pytest.raises(
        ValueError,
        match="target_uri or target_celex",
    ):
        EurLexLegalBasis(
            kind=(
                EurLexLegalBasisKind.TREATY_ARTICLE
            ),
            source_predicate="work_based_on_treaty",
        )


def test_normalizes_optional_legal_basis_values() -> None:
    legal_basis = EurLexLegalBasis(
        kind=EurLexLegalBasisKind.TREATY_ARTICLE,
        target_uri=(
            " http://data.europa.eu/eli/"
            "treaty/tfeu_2012/art_114/oj "
        ),
        treaty=" TFEU ",
        article=" 114 ",
        paragraph="  1 ",
        label=" Article 114(1)   TFEU ",
        source_predicate=" work_based_on_treaty ",
    )

    assert legal_basis.treaty == "TFEU"
    assert legal_basis.article == "114"
    assert legal_basis.paragraph == "1"
    assert legal_basis.label == (
        "Article 114(1) TFEU"
    )


def test_accepts_secondary_act_celex_basis() -> None:
    legal_basis = EurLexLegalBasis(
        kind=(
            EurLexLegalBasisKind.SECONDARY_ACT
        ),
        target_celex=CelexIdentifier.parse(
            "32013R0575"
        ),
        source_predicate=(
            "work_based_on_legal_resource"
        ),
    )

    assert legal_basis.target_celex is not None


def test_deduplicates_legal_bases() -> None:
    legal_basis = EurLexLegalBasis(
        kind=EurLexLegalBasisKind.TREATY_ARTICLE,
        target_uri=(
            "http://data.europa.eu/eli/"
            "treaty/tfeu_2012/art_114/oj"
        ),
        source_predicate="work_based_on_treaty",
    )

    assert normalize_legal_bases(
        (legal_basis, legal_basis)
    ) == (legal_basis,)


def test_maps_legal_basis_predicate() -> None:
    assert legal_basis_kind_from_predicate(
        "work_based_on_treaty"
    ) is EurLexLegalBasisKind.TREATY_ARTICLE
