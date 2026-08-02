"""Typed English titles extracted from EUR-Lex."""

from __future__ import annotations

from enum import StrEnum


class EurLexTitleKind(StrEnum):
    """Describe the source role of one EUR-Lex title."""

    OFFICIAL = "OFFICIAL"
    SHORT = "SHORT"
    ALTERNATIVE = "ALTERNATIVE"
    UNKNOWN = "UNKNOWN"


_TITLE_KIND_BY_PREDICATE = {
    "work_title": EurLexTitleKind.OFFICIAL,
    "expression_title": EurLexTitleKind.OFFICIAL,
    "resource_legal_title": EurLexTitleKind.OFFICIAL,
    "title": EurLexTitleKind.OFFICIAL,
    "work_title_short": EurLexTitleKind.SHORT,
    "expression_title_short": EurLexTitleKind.SHORT,
    "resource_legal_title_short": EurLexTitleKind.SHORT,
    "title_short": EurLexTitleKind.SHORT,
    "short_title": EurLexTitleKind.SHORT,
    "work_title_alternative": (
        EurLexTitleKind.ALTERNATIVE
    ),
    "expression_title_alternative": (
        EurLexTitleKind.ALTERNATIVE
    ),
    "resource_legal_title_alternative": (
        EurLexTitleKind.ALTERNATIVE
    ),
    "title_alternative": (
        EurLexTitleKind.ALTERNATIVE
    ),
    "alternative_title": (
        EurLexTitleKind.ALTERNATIVE
    ),
}


def title_kind_from_predicate(
    predicate: str,
) -> EurLexTitleKind | None:
    """Resolve a supported RDF title predicate."""
    if not isinstance(predicate, str):
        raise TypeError(
            "predicate must be a string"
        )

    normalized = (
        predicate.strip()
        .replace("-", "_")
        .casefold()
    )
    if not normalized:
        return None

    return _TITLE_KIND_BY_PREDICATE.get(
        normalized
    )
