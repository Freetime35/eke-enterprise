"""Explicit English legal definitions extracted from EUR-Lex content."""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.localization import LanguageCode


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(f"{name} must not be empty")

    return normalized


def _normalize_optional_text(
    value: str | None,
    *,
    name: str,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string or None"
        )

    normalized = " ".join(value.split())
    return normalized or None


@dataclass(frozen=True, slots=True)
class EurLexLegalDefinition:
    """Represent one explicit source-backed legal definition."""

    term: str
    definition: str
    source_node_id: str
    source_text: str
    language: LanguageCode
    article_node_id: str | None = None
    paragraph_node_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "term",
            "definition",
            "source_node_id",
            "source_text",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        for name in (
            "article_node_id",
            "paragraph_node_id",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if not isinstance(
            self.language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode"
            )

        if self.language != LanguageCode("en"):
            raise ValueError(
                "legal definitions must be English"
            )

    @property
    def normalized_term(self) -> str:
        """Return a case-insensitive lookup key."""
        return self.term.casefold()


@dataclass(frozen=True, slots=True)
class EurLexLegalDefinitions:
    """Contain explicit definitions from one document."""

    definitions: tuple[
        EurLexLegalDefinition,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.definitions,
            tuple,
        ):
            raise TypeError(
                "definitions must be a tuple"
            )

        if any(
            not isinstance(
                definition,
                EurLexLegalDefinition,
            )
            for definition in self.definitions
        ):
            raise TypeError(
                "definitions must contain "
                "EurLexLegalDefinition values"
            )

    def definition_by_term(
        self,
        term: str,
    ) -> EurLexLegalDefinition | None:
        """Return the first exact normalized term match."""
        normalized = _normalize_required_text(
            term,
            name="term",
        ).casefold()

        return next(
            (
                definition
                for definition in self.definitions
                if definition.normalized_term
                == normalized
            ),
            None,
        )

    def definitions_for_article(
        self,
        article_node_id: str,
    ) -> tuple[EurLexLegalDefinition, ...]:
        """Return definitions attached to one article."""
        normalized = _normalize_required_text(
            article_node_id,
            name="article_node_id",
        )

        return tuple(
            definition
            for definition in self.definitions
            if definition.article_node_id
            == normalized
        )


def normalize_legal_definitions(
    definitions: tuple[
        EurLexLegalDefinition,
        ...,
    ],
) -> EurLexLegalDefinitions:
    """Deduplicate definitions while preserving source order."""
    if not isinstance(definitions, tuple):
        raise TypeError(
            "definitions must be a tuple"
        )

    if any(
        not isinstance(
            definition,
            EurLexLegalDefinition,
        )
        for definition in definitions
    ):
        raise TypeError(
            "definitions must contain "
            "EurLexLegalDefinition values"
        )

    return EurLexLegalDefinitions(
        definitions=tuple(
            dict.fromkeys(definitions)
        )
    )
