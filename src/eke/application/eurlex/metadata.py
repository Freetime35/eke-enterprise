"""Transport-neutral EUR-Lex metadata representation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


@dataclass(frozen=True, slots=True)
class EurLexTitle:
    """Represent one localized title extracted from EUR-Lex."""

    language: LanguageCode | None
    value: str

    def __post_init__(self) -> None:
        if (
            self.language is not None
            and not isinstance(self.language, LanguageCode)
        ):
            raise TypeError(
                "language must be a LanguageCode or None"
            )
        if not isinstance(self.value, str):
            raise TypeError("value must be a string")

        normalized = " ".join(self.value.split())
        if not normalized:
            raise ValueError("value must not be empty")

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class EurLexMetadata:
    """Represent stable metadata parsed from one Cellar notice."""

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
                "titles must contain only EurLexTitle values"
            )
        if any(
            not isinstance(language, LanguageCode)
            for language in self.languages
        ):
            raise TypeError(
                "languages must contain only LanguageCode values"
            )

        for field_name in (
            "resource_type_uri",
            "status_uri",
        ):
            value = getattr(self, field_name)
            if value is not None:
                if not isinstance(value, str):
                    raise TypeError(
                        f"{field_name} must be a string or None"
                    )
                if not value.strip():
                    raise ValueError(
                        f"{field_name} must not be empty"
                    )

        if any(
            not isinstance(uri, str) or not uri.strip()
            for uri in self.eurovoc_concept_uris
        ):
            raise ValueError(
                "eurovoc_concept_uris must contain "
                "non-empty strings"
            )
