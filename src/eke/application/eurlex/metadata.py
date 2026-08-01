"""Transport-neutral EUR-Lex metadata representation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.application.eurlex.enrichment import (
    EurLexClassification,
    EurLexRelationship,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


@dataclass(frozen=True, slots=True)
class EurLexTitle:
    language: LanguageCode | None
    value: str

    def __post_init__(self) -> None:
        if self.language is not None and not isinstance(
            self.language, LanguageCode
        ):
            raise TypeError("language must be a LanguageCode or None")
        normalized = " ".join(self.value.split())
        if not normalized:
            raise ValueError("value must not be empty")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class EurLexMetadata:
    celex_identifier: CelexIdentifier
    titles: tuple[EurLexTitle, ...] = ()
    document_date: date | None = None
    publication_date: date | None = None
    entry_into_force_date: date | None = None
    end_of_validity_date: date | None = None
    languages: tuple[LanguageCode, ...] = ()
    resource_type_uri: str | None = None
    status_uri: str | None = None
    eurovoc_concept_uris: tuple[str, ...] = ()
    classifications: tuple[EurLexClassification, ...] = ()
    relationships: tuple[EurLexRelationship, ...] = ()
