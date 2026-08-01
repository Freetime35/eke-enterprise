"""CELEX identifier parsing and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from eke.domain.identity.business_identifier import BusinessIdentifier
from eke.domain.identity.identifier_scheme import IdentifierScheme

_CELEX_PATTERN = re.compile(
    r"^(?P<sector>[0-9E])"
    r"(?P<year>[0-9]{4})"
    r"(?P<document_type>[A-Z]{1,2})"
    r"(?P<document_number>[0-9]{4})$"
)


class CelexSector(StrEnum):
    """Represent the leading CELEX sector code."""

    CONSOLIDATED_TEXTS = "0"
    TREATIES = "1"
    INTERNATIONAL_AGREEMENTS = "2"
    LEGISLATION = "3"
    COMPLEMENTARY_LEGISLATION = "4"
    PREPARATORY_ACTS = "5"
    CASE_LAW = "6"
    NATIONAL_IMPLEMENTATION = "7"
    NATIONAL_CASE_LAW = "8"
    PARLIAMENTARY_QUESTIONS = "9"
    EFTA = "E"


@dataclass(frozen=True, slots=True)
class CelexIdentifier:
    """Immutable parsed CELEX identifier in standard form."""

    sector: CelexSector
    year: int
    document_type: str
    document_number: str

    def __post_init__(self) -> None:
        if not isinstance(self.sector, CelexSector):
            raise TypeError("sector must be a CelexSector")
        if not isinstance(self.year, int):
            raise TypeError("year must be an integer")
        if not 1000 <= self.year <= 9999:
            raise ValueError(
                "year must be a four-digit positive year"
            )
        if not isinstance(self.document_type, str):
            raise TypeError("document_type must be a string")
        if not re.fullmatch(
            r"[A-Z]{1,2}",
            self.document_type,
        ):
            raise ValueError(
                "document_type must contain one or two "
                "uppercase letters"
            )
        if not isinstance(self.document_number, str):
            raise TypeError("document_number must be a string")
        if not re.fullmatch(
            r"[0-9]{4}",
            self.document_number,
        ):
            raise ValueError(
                "document_number must contain four digits"
            )

    @classmethod
    def parse(cls, value: str) -> CelexIdentifier:
        """Parse a standard-form CELEX identifier."""
        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized = value.strip().upper()
        if normalized.startswith("CELEX:"):
            normalized = normalized.removeprefix("CELEX:")

        match = _CELEX_PATTERN.fullmatch(normalized)
        if match is None:
            raise ValueError(
                "value must be a standard-form CELEX identifier"
            )

        return cls(
            sector=CelexSector(match.group("sector")),
            year=int(match.group("year")),
            document_type=match.group("document_type"),
            document_number=match.group("document_number"),
        )

    @property
    def value(self) -> str:
        """Return the canonical CELEX string."""
        return (
            f"{self.sector.value}"
            f"{self.year:04d}"
            f"{self.document_type}"
            f"{self.document_number}"
        )

    def to_business_identifier(self) -> BusinessIdentifier:
        """Convert to the generic domain identifier representation."""
        return BusinessIdentifier(
            scheme=IdentifierScheme.CELEX,
            value=self.value,
        )

    def __str__(self) -> str:
        return self.value
