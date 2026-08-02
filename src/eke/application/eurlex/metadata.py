"""Transport-neutral EUR-Lex metadata representation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.application.eurlex.enrichment import (
    EurLexClassification,
    EurLexRelationship,
)
from eke.application.eurlex.institutional_provenance import (
    EurLexInstitution,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


@dataclass(frozen=True, slots=True)
class EurLexTitle:
    """Represent one localized EUR-Lex title."""

    language: LanguageCode | None
    value: str

    def __post_init__(self) -> None:
        if self.language is not None and not isinstance(
            self.language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode or None"
            )

        normalized = " ".join(self.value.split())
        if not normalized:
            raise ValueError("value must not be empty")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class EurLexOfficialJournalReference:
    """Represent publication coordinates in the Official Journal."""

    uri: str | None = None
    number: str | None = None
    page_first: str | None = None
    page_last: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("uri", self.uri),
            ("number", self.number),
            ("page_first", self.page_first),
            ("page_last", self.page_last),
        ):
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"{name} must be a string or None"
                )
            if isinstance(value, str):
                normalized = " ".join(value.split())
                object.__setattr__(
                    self,
                    name,
                    normalized or None,
                )


@dataclass(frozen=True, slots=True)
class EurLexMetadataCompleteness:
    """Describe completeness of stable EUR-Lex core metadata."""

    score: float
    present_fields: tuple[str, ...]
    missing_fields: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.score, float):
            raise TypeError("score must be a float")
        if self.score < 0.0 or self.score > 1.0:
            raise ValueError(
                "score must be between zero and one"
            )
        if set(self.present_fields) & set(
            self.missing_fields
        ):
            raise ValueError(
                "present and missing fields must not overlap"
            )


@dataclass(frozen=True, slots=True)
class EurLexMetadata:
    """Represent normalized metadata extracted from EUR-Lex."""

    celex_identifier: CelexIdentifier
    titles: tuple[EurLexTitle, ...] = ()
    document_date: date | None = None
    publication_date: date | None = None
    entry_into_force_date: date | None = None
    end_of_validity_date: date | None = None
    languages: tuple[LanguageCode, ...] = ()
    resource_type_uri: str | None = None
    status_uri: str | None = None
    eli_uri: str | None = None
    cellar_uri: str | None = None
    official_journal: (
        EurLexOfficialJournalReference | None
    ) = None
    responsible_agent_uris: tuple[str, ...] = ()
    institutions: tuple[EurLexInstitution, ...] = ()
    eurovoc_concept_uris: tuple[str, ...] = ()
    classifications: tuple[EurLexClassification, ...] = ()
    relationships: tuple[EurLexRelationship, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.celex_identifier,
            CelexIdentifier,
        ):
            raise TypeError(
                "celex_identifier must be a CelexIdentifier"
            )

        if any(
            not isinstance(title, EurLexTitle)
            for title in self.titles
        ):
            raise TypeError(
                "titles must contain EurLexTitle values"
            )

        for name, value in (
            ("document_date", self.document_date),
            ("publication_date", self.publication_date),
            (
                "entry_into_force_date",
                self.entry_into_force_date,
            ),
            (
                "end_of_validity_date",
                self.end_of_validity_date,
            ),
        ):
            if value is not None and not isinstance(value, date):
                raise TypeError(
                    f"{name} must be a date or None"
                )

        if any(
            not isinstance(language, LanguageCode)
            for language in self.languages
        ):
            raise TypeError(
                "languages must contain LanguageCode values"
            )

        for field_name, text_value in (
            ("resource_type_uri", self.resource_type_uri),
            ("status_uri", self.status_uri),
            ("eli_uri", self.eli_uri),
            ("cellar_uri", self.cellar_uri),
        ):
            if (
                text_value is not None
                and not isinstance(text_value, str)
            ):
                raise TypeError(
                    f"{field_name} must be a string or None"
                )

        if (
            self.official_journal is not None
            and not isinstance(
                self.official_journal,
                EurLexOfficialJournalReference,
            )
        ):
            raise TypeError(
                "official_journal must be an "
                "EurLexOfficialJournalReference or None"
            )

        if any(
            not isinstance(
                institution,
                EurLexInstitution,
            )
            for institution in self.institutions
        ):
            raise TypeError(
                "institutions must contain "
                "EurLexInstitution values"
            )

        for name, values in (
            (
                "responsible_agent_uris",
                self.responsible_agent_uris,
            ),
            (
                "eurovoc_concept_uris",
                self.eurovoc_concept_uris,
            ),
        ):
            if any(
                not isinstance(value, str)
                or not value.strip()
                for value in values
            ):
                raise TypeError(
                    f"{name} must contain non-empty strings"
                )

    def assess_completeness(
        self,
    ) -> EurLexMetadataCompleteness:
        """Assess stable core metadata without inventing values."""
        fields = {
            "localized_title": any(
                title.language is not None
                for title in self.titles
            ),
            "document_date": self.document_date is not None,
            "publication_date": (
                self.publication_date is not None
            ),
            "language": bool(self.languages),
            "resource_type": (
                self.resource_type_uri is not None
            ),
            "status": self.status_uri is not None,
            "eli": self.eli_uri is not None,
            "cellar": self.cellar_uri is not None,
            "official_journal": (
                self.official_journal is not None
            ),
            "responsible_agent": bool(
                self.responsible_agent_uris
            ),
        }
        present = tuple(
            name
            for name, available in fields.items()
            if available
        )
        missing = tuple(
            name
            for name, available in fields.items()
            if not available
        )

        return EurLexMetadataCompleteness(
            score=len(present) / len(fields),
            present_fields=present,
            missing_fields=missing,
        )
