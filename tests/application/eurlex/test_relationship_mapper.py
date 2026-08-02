"""Tests for EUR-Lex relationship predicate mapping."""

import pytest

from eke.application.eurlex.relationship_mapper import (
    relationship_type_from_predicate,
)
from eke.domain.relationships import RelationshipType


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        (
            "work_amends_work",
            RelationshipType.AMENDS,
        ),
        (
            "work_repeals_work",
            RelationshipType.REPEALS,
        ),
        (
            "work_cites_work",
            RelationshipType.CITES,
        ),
        (
            "work_has_legal_basis",
            RelationshipType.LEGAL_BASIS,
        ),
        (
            "work_corrected_by_work",
            RelationshipType.CORRECTED_BY,
        ),
    ],
)
def test_maps_known_predicates(
    predicate: str,
    expected: RelationshipType,
) -> None:
    assert (
        relationship_type_from_predicate(
            predicate
        )
        is expected
    )


def test_unknown_predicate_is_ignored() -> None:
    assert (
        relationship_type_from_predicate(
            "work_unknown_work"
        )
        is None
    )
