"""Map EUR-Lex CDM predicates to canonical relationships."""

from __future__ import annotations

from eke.domain.relationships import RelationshipType

_RELATIONSHIP_TYPES = {
    "work_amends_work": RelationshipType.AMENDS,
    "work_amended_by_work": RelationshipType.AMENDED_BY,
    "work_repeals_work": RelationshipType.REPEALS,
    "work_repealed_by_work": RelationshipType.REPEALED_BY,
    "work_cites_work": RelationshipType.CITES,
    "work_is_based_on_work": RelationshipType.LEGAL_BASIS,
    "work_has_legal_basis": RelationshipType.LEGAL_BASIS,
    "work_consolidates_work": RelationshipType.CONSOLIDATES,
    "work_consolidated_by_work": (
        RelationshipType.CONSOLIDATED_BY
    ),
    "work_implements_work": RelationshipType.IMPLEMENTS,
    "work_implemented_by_work": (
        RelationshipType.IMPLEMENTED_BY
    ),
    "work_transposes_work": (
        RelationshipType.TRANSPOSITION_OF
    ),
    "work_transposed_by_work": (
        RelationshipType.TRANSPOSED_BY
    ),
    "work_corrects_work": RelationshipType.CORRECTS,
    "work_corrected_by_work": (
        RelationshipType.CORRECTED_BY
    ),
    "work_related_to_work": RelationshipType.RELATED_TO,
}


def relationship_type_from_predicate(
    predicate: str,
) -> RelationshipType | None:
    """Return the canonical type for one CDM predicate."""
    if not isinstance(predicate, str):
        raise TypeError("predicate must be a string")

    normalized = (
        predicate.strip()
        .replace("-", "_")
        .casefold()
    )
    if not normalized:
        return None

    return _RELATIONSHIP_TYPES.get(normalized)
