"""Tests for standard-form CELEX identifiers."""

from __future__ import annotations

import pytest

from eke.domain.identity import (
    CelexIdentifier,
    CelexSector,
    IdentifierScheme,
)


@pytest.mark.parametrize(
    ("value", "sector", "year", "document_type", "number"),
    [
        (
            "32023R1114",
            CelexSector.LEGISLATION,
            2023,
            "R",
            "1114",
        ),
        (
            "52016DC0205",
            CelexSector.PREPARATORY_ACTS,
            2016,
            "DC",
            "0205",
        ),
        (
            "61992CJ0396",
            CelexSector.CASE_LAW,
            1992,
            "CJ",
            "0396",
        ),
    ],
)
def test_parse_standard_celex_identifiers(
    value: str,
    sector: CelexSector,
    year: int,
    document_type: str,
    number: str,
) -> None:
    identifier = CelexIdentifier.parse(value)

    assert identifier.sector is sector
    assert identifier.year == year
    assert identifier.document_type == document_type
    assert identifier.document_number == number
    assert identifier.value == value
    assert str(identifier) == value


def test_parse_normalizes_prefix_case_and_whitespace() -> None:
    identifier = CelexIdentifier.parse(
        "  celex:32023r1114  "
    )

    assert identifier.value == "32023R1114"


def test_convert_to_business_identifier() -> None:
    identifier = CelexIdentifier.parse("32023R1114")

    business_identifier = identifier.to_business_identifier()

    assert business_identifier.scheme is IdentifierScheme.CELEX
    assert business_identifier.value == "32023R1114"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "32023R111",
        "32023R11145",
        "3202R1114",
        "X2023R1114",
        "32023ABC1114",
        "32023R11A4",
        "CELEX:",
        "32023R1114-20240101",
    ],
)
def test_parse_rejects_non_standard_forms(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "value must be a standard-form CELEX identifier"
        ),
    ):
        CelexIdentifier.parse(value)


def test_parse_rejects_non_string() -> None:
    with pytest.raises(
        TypeError,
        match="value must be a string",
    ):
        CelexIdentifier.parse(123)  # type: ignore[arg-type]


def test_constructor_rejects_invalid_document_type() -> None:
    with pytest.raises(
        ValueError,
        match="document_type",
    ):
        CelexIdentifier(
            sector=CelexSector.LEGISLATION,
            year=2023,
            document_type="reg",
            document_number="1114",
        )


def test_constructor_rejects_invalid_document_number() -> None:
    with pytest.raises(
        ValueError,
        match="document_number",
    ):
        CelexIdentifier(
            sector=CelexSector.LEGISLATION,
            year=2023,
            document_type="R",
            document_number="114",
        )
