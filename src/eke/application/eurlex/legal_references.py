"""Explicit source-backed EUR-Lex legal references."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.identity import CelexIdentifier


class EurLexLegalReferenceKind(StrEnum):
    """Canonical kinds of legal references."""

    CITES = "CITES"
    LEGAL_BASIS = "LEGAL_BASIS"
    TREATY_BASIS = "TREATY_BASIS"
    ARTICLE_REFERENCE = "ARTICLE_REFERENCE"
    PREPARATORY_ACT = "PREPARATORY_ACT"
    RELATED_ACT = "RELATED_ACT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EurLexLegalReference:
    """Represent one explicit reference found in EUR-Lex metadata."""

    kind: EurLexLegalReferenceKind
    source_predicate: str
    target_celex: CelexIdentifier | None = None
    target_uri: str | None = None
    article: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            EurLexLegalReferenceKind,
        ):
            raise TypeError(
                "kind must be an EurLexLegalReferenceKind"
            )

        if not isinstance(self.source_predicate, str):
            raise TypeError(
                "source_predicate must be a string"
            )
        source_predicate = " ".join(
            self.source_predicate.split()
        )
        if not source_predicate:
            raise ValueError(
                "source_predicate must not be empty"
            )
        object.__setattr__(
            self,
            "source_predicate",
            source_predicate,
        )

        if (
            self.target_celex is not None
            and not isinstance(
                self.target_celex,
                CelexIdentifier,
            )
        ):
            raise TypeError(
                "target_celex must be a "
                "CelexIdentifier or None"
            )

        if self.target_uri is not None:
            if not isinstance(self.target_uri, str):
                raise TypeError(
                    "target_uri must be a string or None"
                )
            target_uri = self.target_uri.strip()
            object.__setattr__(
                self,
                "target_uri",
                target_uri or None,
            )

        if self.article is not None:
            if not isinstance(self.article, str):
                raise TypeError(
                    "article must be a string or None"
                )
            article = " ".join(self.article.split())
            object.__setattr__(
                self,
                "article",
                article or None,
            )

        if (
            self.target_celex is None
            and self.target_uri is None
        ):
            raise ValueError(
                "target_celex or target_uri is required"
            )


_REFERENCE_KIND_BY_PREDICATE: dict[
    str,
    EurLexLegalReferenceKind,
] = {
    "work_cites_work": EurLexLegalReferenceKind.CITES,
    "cites": EurLexLegalReferenceKind.CITES,
    "resource_legal_cites": (
        EurLexLegalReferenceKind.CITES
    ),
    "work_based_on_legal_resource": (
        EurLexLegalReferenceKind.LEGAL_BASIS
    ),
    "legal_basis": (
        EurLexLegalReferenceKind.LEGAL_BASIS
    ),
    "work_based_on_treaty": (
        EurLexLegalReferenceKind.TREATY_BASIS
    ),
    "treaty_basis": (
        EurLexLegalReferenceKind.TREATY_BASIS
    ),
    "article_reference": (
        EurLexLegalReferenceKind.ARTICLE_REFERENCE
    ),
    "work_refers_to_article": (
        EurLexLegalReferenceKind.ARTICLE_REFERENCE
    ),
    "work_has_preparatory_act": (
        EurLexLegalReferenceKind.PREPARATORY_ACT
    ),
    "preparatory_act": (
        EurLexLegalReferenceKind.PREPARATORY_ACT
    ),
    "work_related_to_work": (
        EurLexLegalReferenceKind.RELATED_ACT
    ),
    "related_act": (
        EurLexLegalReferenceKind.RELATED_ACT
    ),
}


def legal_reference_kind_from_predicate(
    predicate: str,
) -> EurLexLegalReferenceKind | None:
    """Resolve a supported legal-reference predicate."""
    if not isinstance(predicate, str):
        raise TypeError("predicate must be a string")

    normalized = (
        predicate.strip()
        .replace("-", "_")
        .casefold()
    )
    if not normalized:
        return None

    return _REFERENCE_KIND_BY_PREDICATE.get(
        normalized
    )


def normalize_legal_references(
    references: tuple[EurLexLegalReference, ...],
) -> tuple[EurLexLegalReference, ...]:
    """Deduplicate references while preserving source order."""
    if not isinstance(references, tuple):
        raise TypeError("references must be a tuple")

    if any(
        not isinstance(
            reference,
            EurLexLegalReference,
        )
        for reference in references
    ):
        raise TypeError(
            "references must contain "
            "EurLexLegalReference values"
        )

    return tuple(dict.fromkeys(references))
