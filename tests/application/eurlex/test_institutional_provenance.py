"""Tests for EUR-Lex institution normalization."""

import pytest

from eke.application.eurlex.institutional_provenance import (
    EurLexInstitutionType,
    institution_from_uri,
    normalize_institutions,
)
from eke.domain.provenance import ProvenanceSource


@pytest.mark.parametrize(
    ("token", "name", "source"),
    [
        (
            "ECB",
            "European Central Bank",
            ProvenanceSource.ECB,
        ),
        (
            "EBA",
            "European Banking Authority",
            ProvenanceSource.EBA,
        ),
        (
            "ESMA",
            "European Securities and Markets Authority",
            ProvenanceSource.ESMA,
        ),
        (
            "EIOPA",
            (
                "European Insurance and Occupational "
                "Pensions Authority"
            ),
            ProvenanceSource.EIOPA,
        ),
        (
            "SRB",
            "Single Resolution Board",
            ProvenanceSource.SRB,
        ),
    ],
)
def test_normalizes_financial_authorities(
    token: str,
    name: str,
    source: ProvenanceSource,
) -> None:
    institution = institution_from_uri(
        "http://publications.europa.eu/"
        "resource/authority/corporate-body/"
        f"{token}"
    )

    assert institution.name == name
    assert institution.provenance_source is source


def test_unknown_institution_is_preserved() -> None:
    institution = institution_from_uri(
        "https://example.test/corporate-body/NEW_BODY"
    )

    assert (
        institution.institution_type
        is EurLexInstitutionType.UNKNOWN
    )
    assert institution.provenance_source is None


def test_normalization_deduplicates_uri() -> None:
    uri = (
        "http://publications.europa.eu/"
        "resource/authority/corporate-body/ECB"
    )

    assert len(
        normalize_institutions((uri, uri))
    ) == 1
