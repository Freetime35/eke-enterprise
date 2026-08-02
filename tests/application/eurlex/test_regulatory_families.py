"""Tests for financial regulatory family detection."""

import pytest

from eke.application.eurlex import (
    EurLexRegulatoryFamily,
    EurLexTitle,
    RegulatoryFamilyEvidenceKind,
    detect_regulatory_families,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        (
            "Digital Operational Resilience Act (DORA)",
            EurLexRegulatoryFamily.DORA,
        ),
        (
            "Markets in Crypto-assets Regulation",
            EurLexRegulatoryFamily.MICA,
        ),
        (
            "Capital Requirements Regulation (CRR)",
            EurLexRegulatoryFamily.CRR,
        ),
        (
            "Markets in Financial Instruments "
            "Directive II (MiFID II)",
            EurLexRegulatoryFamily.MIFID_II,
        ),
        (
            "European Market Infrastructure "
            "Regulation (EMIR)",
            EurLexRegulatoryFamily.EMIR,
        ),
    ],
)
def test_detects_explicit_title_evidence(
    title: str,
    expected: EurLexRegulatoryFamily,
) -> None:
    matches = detect_regulatory_families(
        CelexIdentifier.parse("32020R0001"),
        (
            EurLexTitle(
                LanguageCode("en"),
                title,
            ),
        ),
    )

    assert len(matches) == 1
    assert matches[0].family is expected
    assert (
        matches[0].evidence_kind
        is RegulatoryFamilyEvidenceKind.TITLE
    )


def test_detects_known_celex() -> None:
    matches = detect_regulatory_families(
        CelexIdentifier.parse("32023R1114"),
        (),
    )

    assert matches[0].family is (
        EurLexRegulatoryFamily.MICA
    )
    assert (
        matches[0].evidence_kind
        is RegulatoryFamilyEvidenceKind.CELEX
    )


def test_ignores_ambiguous_financial_words() -> None:
    matches = detect_regulatory_families(
        CelexIdentifier.parse("32020R0001"),
        (
            EurLexTitle(
                LanguageCode("en"),
                "Regulation on capital and payments",
            ),
        ),
    )

    assert matches == ()


def test_detects_multiple_unique_families() -> None:
    matches = detect_regulatory_families(
        CelexIdentifier.parse("32020L0001"),
        (
            EurLexTitle(
                LanguageCode("en"),
                "Directive amending CRD and BRRD",
            ),
            EurLexTitle(
                LanguageCode("en"),
                "BRRD amendment",
            ),
        ),
    )

    assert tuple(
        match.family for match in matches
    ) == (
        EurLexRegulatoryFamily.CRD,
        EurLexRegulatoryFamily.BRRD,
    )
