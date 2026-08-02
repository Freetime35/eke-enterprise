"""Explicit source-backed EUR-Lex legal bases."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.identity import CelexIdentifier


class EurLexLegalBasisKind(StrEnum):
    """Canonical kinds of legal bases."""

    TREATY_ARTICLE = "TREATY_ARTICLE"
    TREATY = "TREATY"
    PROTOCOL = "PROTOCOL"
    CHARTER_ARTICLE = "CHARTER_ARTICLE"
    SECONDARY_ACT = "SECONDARY_ACT"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class EurLexLegalBasis:
    """Represent one explicit legal basis."""

    kind: EurLexLegalBasisKind
    source_predicate: str
    target_uri: str | None = None
    target_celex: CelexIdentifier | None = None
    treaty: str | None = None
    article: str | None = None
    paragraph: str | None = None
    label: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            EurLexLegalBasisKind,
        ):
            raise TypeError(
                "kind must be an EurLexLegalBasisKind"
            )

        if not isinstance(
            self.source_predicate,
            str,
        ):
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

        for name in (
            "target_uri",
            "treaty",
            "article",
            "paragraph",
            "label",
        ):
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(value, str):
                raise TypeError(
                    f"{name} must be a string or None"
                )

            normalized = " ".join(value.split())
            object.__setattr__(
                self,
                name,
                normalized or None,
            )

        if (
            self.target_uri is None
            and self.target_celex is None
        ):
            raise ValueError(
                "target_uri or target_celex is required"
            )


_LEGAL_BASIS_KIND_BY_PREDICATE: dict[
    str,
    EurLexLegalBasisKind,
] = {
    "work_based_on_treaty": (
        EurLexLegalBasisKind.TREATY_ARTICLE
    ),
    "treaty_basis": (
        EurLexLegalBasisKind.TREATY_ARTICLE
    ),
    "resource_legal_based_on_treaty": (
        EurLexLegalBasisKind.TREATY_ARTICLE
    ),
    "work_based_on_legal_resource": (
        EurLexLegalBasisKind.SECONDARY_ACT
    ),
    "resource_legal_based_on": (
        EurLexLegalBasisKind.SECONDARY_ACT
    ),
    "legal_basis": (
        EurLexLegalBasisKind.OTHER
    ),
    "protocol_basis": (
        EurLexLegalBasisKind.PROTOCOL
    ),
    "charter_basis": (
        EurLexLegalBasisKind.CHARTER_ARTICLE
    ),
}


def legal_basis_kind_from_predicate(
    predicate: str,
) -> EurLexLegalBasisKind | None:
    """Resolve a supported legal-basis predicate."""
    if not isinstance(predicate, str):
        raise TypeError("predicate must be a string")

    normalized = (
        predicate.strip()
        .replace("-", "_")
        .casefold()
    )
    if not normalized:
        return None

    return _LEGAL_BASIS_KIND_BY_PREDICATE.get(
        normalized
    )


def normalize_legal_bases(
    legal_bases: tuple[EurLexLegalBasis, ...],
) -> tuple[EurLexLegalBasis, ...]:
    """Deduplicate legal bases while preserving source order."""
    if not isinstance(legal_bases, tuple):
        raise TypeError(
            "legal_bases must be a tuple"
        )

    if any(
        not isinstance(
            legal_basis,
            EurLexLegalBasis,
        )
        for legal_basis in legal_bases
    ):
        raise TypeError(
            "legal_bases must contain "
            "EurLexLegalBasis values"
        )

    return tuple(dict.fromkeys(legal_bases))
