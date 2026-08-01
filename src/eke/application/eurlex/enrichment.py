"""Enrichment metadata used by the full EUR-Lex import pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.domain.relationships import RelationshipType


@dataclass(frozen=True, slots=True)
class EurLexClassification:
    """Represent one labeled EuroVoc concept."""

    uri: str
    code: str
    language: LanguageCode
    label: str

    def __post_init__(self) -> None:
        if not self.uri.strip():
            raise ValueError("uri must not be empty")
        if not self.code.strip():
            raise ValueError("code must not be empty")
        if not self.label.strip():
            raise ValueError("label must not be empty")


@dataclass(frozen=True, slots=True)
class EurLexRelationship:
    """Represent one directed CELEX relationship."""

    target_celex: CelexIdentifier
    relationship_type: RelationshipType
