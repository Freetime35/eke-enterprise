"""Explicit English legal prohibitions extracted from EUR-Lex content."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.localization import LanguageCode


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string"
        )

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(
            f"{name} must not be empty"
        )

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


class EurLexLegalProhibitionKind(StrEnum):
    """Canonical explicit prohibition markers."""

    SHALL_NOT = "SHALL_NOT"
    MUST_NOT = "MUST_NOT"
    MAY_NOT = "MAY_NOT"
    PROHIBITED_FROM = "PROHIBITED_FROM"
    NOT_AUTHORISED_TO = "NOT_AUTHORISED_TO"
    NOT_ALLOWED_TO = "NOT_ALLOWED_TO"


@dataclass(frozen=True, slots=True)
class EurLexLegalProhibition:
    """Represent one explicit source-backed prohibition."""

    subject: str
    action: str
    kind: EurLexLegalProhibitionKind
    source_node_id: str
    source_text: str
    language: LanguageCode
    article_node_id: str | None = None
    paragraph_node_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "subject",
            "action",
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
            self.kind,
            EurLexLegalProhibitionKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalProhibitionKind"
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
                "legal prohibitions must be English"
            )

    @property
    def normalized_subject(self) -> str:
        """Return a case-insensitive subject key."""
        return self.subject.casefold()


@dataclass(frozen=True, slots=True)
class EurLexLegalProhibitions:
    """Contain explicit prohibitions from one document."""

    prohibitions: tuple[
        EurLexLegalProhibition,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.prohibitions,
            tuple,
        ):
            raise TypeError(
                "prohibitions must be a tuple"
            )

        if any(
            not isinstance(
                prohibition,
                EurLexLegalProhibition,
            )
            for prohibition in self.prohibitions
        ):
            raise TypeError(
                "prohibitions must contain "
                "EurLexLegalProhibition values"
            )

    def prohibitions_for_article(
        self,
        article_node_id: str,
    ) -> tuple[EurLexLegalProhibition, ...]:
        """Return prohibitions attached to one article."""
        normalized = _normalize_required_text(
            article_node_id,
            name="article_node_id",
        )

        return tuple(
            prohibition
            for prohibition in self.prohibitions
            if prohibition.article_node_id
            == normalized
        )

    def prohibitions_for_subject(
        self,
        subject: str,
    ) -> tuple[EurLexLegalProhibition, ...]:
        """Return prohibitions for an exact normalized subject."""
        normalized = _normalize_required_text(
            subject,
            name="subject",
        ).casefold()

        return tuple(
            prohibition
            for prohibition in self.prohibitions
            if prohibition.normalized_subject
            == normalized
        )


def normalize_legal_prohibitions(
    prohibitions: tuple[
        EurLexLegalProhibition,
        ...,
    ],
) -> EurLexLegalProhibitions:
    """Deduplicate prohibitions while preserving source order."""
    if not isinstance(prohibitions, tuple):
        raise TypeError(
            "prohibitions must be a tuple"
        )

    if any(
        not isinstance(
            prohibition,
            EurLexLegalProhibition,
        )
        for prohibition in prohibitions
    ):
        raise TypeError(
            "prohibitions must contain "
            "EurLexLegalProhibition values"
        )

    return EurLexLegalProhibitions(
        prohibitions=tuple(
            dict.fromkeys(prohibitions)
        )
    )
