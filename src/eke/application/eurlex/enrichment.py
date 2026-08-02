"""Enrichment metadata used by the full EUR-Lex import pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from eke.application.eurlex.financial_classification import (
    FinancialClassificationCategory,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.domain.relationships import RelationshipType


@dataclass(frozen=True, slots=True)
class EurLexClassification:
    """Represent one labeled financial EuroVoc concept."""

    uri: str
    code: str
    language: LanguageCode
    label: str
    scheme_uri: str | None = None
    broader_uris: tuple[str, ...] = ()
    narrower_uris: tuple[str, ...] = ()
    financial_category: (
        FinancialClassificationCategory | None
    ) = None

    def __post_init__(self) -> None:
        for name, value in (
            ("uri", self.uri),
            ("code", self.code),
            ("label", self.label),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string")
            normalized = " ".join(value.split())
            if not normalized:
                raise ValueError(f"{name} must not be empty")
            object.__setattr__(self, name, normalized)

        if not isinstance(self.language, LanguageCode):
            raise TypeError(
                "language must be a LanguageCode"
            )

        if (
            self.scheme_uri is not None
            and not isinstance(self.scheme_uri, str)
        ):
            raise TypeError(
                "scheme_uri must be a string or None"
            )

        for name, values in (
            ("broader_uris", self.broader_uris),
            ("narrower_uris", self.narrower_uris),
        ):
            if any(
                not isinstance(value, str)
                or not value.strip()
                for value in values
            ):
                raise TypeError(
                    f"{name} must contain non-empty strings"
                )

        if (
            self.financial_category is not None
            and not isinstance(
                self.financial_category,
                FinancialClassificationCategory,
            )
        ):
            raise TypeError(
                "financial_category must be a "
                "FinancialClassificationCategory or None"
            )


@dataclass(frozen=True, slots=True)
class EurLexRelationship:
    """Represent one directed CELEX relationship."""

    target_celex: CelexIdentifier
    relationship_type: RelationshipType
