"""Explicit English legal obligations extracted from EUR-Lex content."""

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


class EurLexLegalObligationKind(StrEnum):
    """Canonical explicit obligation markers."""

    SHALL = "SHALL"
    MUST = "MUST"
    REQUIRED_TO = "REQUIRED_TO"
    HAS_TO = "HAS_TO"


@dataclass(frozen=True, slots=True)
class EurLexLegalObligation:
    """Represent one explicit source-backed obligation."""

    subject: str
    action: str
    kind: EurLexLegalObligationKind
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
            EurLexLegalObligationKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalObligationKind"
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
                "legal obligations must be English"
            )

    @property
    def normalized_subject(self) -> str:
        """Return a case-insensitive subject key."""
        return self.subject.casefold()


@dataclass(frozen=True, slots=True)
class EurLexLegalObligations:
    """Contain explicit obligations from one document."""

    obligations: tuple[
        EurLexLegalObligation,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.obligations,
            tuple,
        ):
            raise TypeError(
                "obligations must be a tuple"
            )

        if any(
            not isinstance(
                obligation,
                EurLexLegalObligation,
            )
            for obligation in self.obligations
        ):
            raise TypeError(
                "obligations must contain "
                "EurLexLegalObligation values"
            )

    def obligations_for_article(
        self,
        article_node_id: str,
    ) -> tuple[EurLexLegalObligation, ...]:
        """Return obligations attached to one article."""
        normalized = _normalize_required_text(
            article_node_id,
            name="article_node_id",
        )

        return tuple(
            obligation
            for obligation in self.obligations
            if obligation.article_node_id
            == normalized
        )

    def obligations_for_subject(
        self,
        subject: str,
    ) -> tuple[EurLexLegalObligation, ...]:
        """Return obligations for an exact normalized subject."""
        normalized = _normalize_required_text(
            subject,
            name="subject",
        ).casefold()

        return tuple(
            obligation
            for obligation in self.obligations
            if obligation.normalized_subject
            == normalized
        )


def normalize_legal_obligations(
    obligations: tuple[
        EurLexLegalObligation,
        ...,
    ],
) -> EurLexLegalObligations:
    """Deduplicate obligations while preserving source order."""
    if not isinstance(obligations, tuple):
        raise TypeError(
            "obligations must be a tuple"
        )

    if any(
        not isinstance(
            obligation,
            EurLexLegalObligation,
        )
        for obligation in obligations
    ):
        raise TypeError(
            "obligations must contain "
            "EurLexLegalObligation values"
        )

    return EurLexLegalObligations(
        obligations=tuple(
            dict.fromkeys(obligations)
        )
    )
