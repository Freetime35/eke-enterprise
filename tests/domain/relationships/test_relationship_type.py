"""Tests for the RelationshipType enumeration."""

from __future__ import annotations

import pytest

from eke.domain.relationships import RelationshipType


def test_relationship_type_members_are_unique() -> None:
    values = [relationship_type.value for relationship_type in RelationshipType]

    assert len(values) == len(set(values))


@pytest.mark.parametrize(
    "relationship_type",
    list(RelationshipType),
)
def test_relationship_type_serializes_to_stable_string(
    relationship_type: RelationshipType,
) -> None:
    assert str(relationship_type) == relationship_type.value


def test_relationship_type_can_be_created_from_valid_string() -> None:
    assert RelationshipType("AMENDS") is RelationshipType.AMENDS


def test_relationship_type_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        RelationshipType("UNKNOWN")
