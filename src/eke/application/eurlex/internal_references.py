"""Explicit English internal references extracted from EUR-Lex content."""

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


class EurLexInternalReferenceKind(StrEnum):
    """Canonical kinds of internal document references."""

    ARTICLE = "ARTICLE"
    PARAGRAPH = "PARAGRAPH"
    SUBPARAGRAPH = "SUBPARAGRAPH"
    POINT = "POINT"
    CHAPTER = "CHAPTER"
    SECTION = "SECTION"
    PART = "PART"
    TITLE = "TITLE"
    ANNEX = "ANNEX"
    APPENDIX = "APPENDIX"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class EurLexInternalReference:
    """Represent one explicit source-backed internal reference."""

    kind: EurLexInternalReferenceKind
    source_node_id: str
    source_text: str
    reference_text: str
    target_ordinal: str
    language: LanguageCode
    target_node_id: str | None = None
    article_node_id: str | None = None
    paragraph_node_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            EurLexInternalReferenceKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexInternalReferenceKind"
            )

        for name in (
            "source_node_id",
            "source_text",
            "reference_text",
            "target_ordinal",
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
            "target_node_id",
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
                "internal references must be English"
            )

    @property
    def is_resolved(self) -> bool:
        """Return whether the reference has one resolved target."""
        return self.target_node_id is not None


@dataclass(frozen=True, slots=True)
class EurLexInternalReferences:
    """Contain internal references from one document."""

    references: tuple[
        EurLexInternalReference,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.references,
            tuple,
        ):
            raise TypeError(
                "references must be a tuple"
            )

        if any(
            not isinstance(
                reference,
                EurLexInternalReference,
            )
            for reference in self.references
        ):
            raise TypeError(
                "references must contain "
                "EurLexInternalReference values"
            )

    def references_from_node(
        self,
        source_node_id: str,
    ) -> tuple[EurLexInternalReference, ...]:
        """Return references emitted by one source node."""
        normalized = _normalize_required_text(
            source_node_id,
            name="source_node_id",
        )

        return tuple(
            reference
            for reference in self.references
            if reference.source_node_id
            == normalized
        )

    def references_to_node(
        self,
        target_node_id: str,
    ) -> tuple[EurLexInternalReference, ...]:
        """Return references resolved to one target node."""
        normalized = _normalize_required_text(
            target_node_id,
            name="target_node_id",
        )

        return tuple(
            reference
            for reference in self.references
            if reference.target_node_id
            == normalized
        )

    def references_for_article(
        self,
        article_node_id: str,
    ) -> tuple[EurLexInternalReference, ...]:
        """Return references emitted inside one article."""
        normalized = _normalize_required_text(
            article_node_id,
            name="article_node_id",
        )

        return tuple(
            reference
            for reference in self.references
            if reference.article_node_id
            == normalized
        )

    def unresolved_references(
        self,
    ) -> tuple[EurLexInternalReference, ...]:
        """Return references without a unique resolved target."""
        return tuple(
            reference
            for reference in self.references
            if not reference.is_resolved
        )


def normalize_internal_references(
    references: tuple[
        EurLexInternalReference,
        ...,
    ],
) -> EurLexInternalReferences:
    """Deduplicate references while preserving source order."""
    if not isinstance(references, tuple):
        raise TypeError(
            "references must be a tuple"
        )

    if any(
        not isinstance(
            reference,
            EurLexInternalReference,
        )
        for reference in references
    ):
        raise TypeError(
            "references must contain "
            "EurLexInternalReference values"
        )

    return EurLexInternalReferences(
        references=tuple(
            dict.fromkeys(references)
        )
    )
