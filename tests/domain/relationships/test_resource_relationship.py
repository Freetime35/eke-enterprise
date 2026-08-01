"""Tests for the ResourceRelationship business concept."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from eke.domain.identity import ResourceUUID
from eke.domain.relationships import (
    RelationshipType,
    ResourceRelationship,
)
from eke.domain.temporal import ValidityPeriod


@pytest.fixture
def source_uuid() -> ResourceUUID:
    return ResourceUUID.generate()


@pytest.fixture
def target_uuid() -> ResourceUUID:
    return ResourceUUID.generate()


def test_create_resource_relationship(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.AMENDS,
    )

    assert relationship.source == source_uuid
    assert relationship.target == target_uuid
    assert relationship.relationship_type is RelationshipType.AMENDS
    assert relationship.validity == ValidityPeriod()


def test_self_relationship_is_rejected(
    source_uuid: ResourceUUID,
) -> None:
    with pytest.raises(
        ValueError,
        match="source and target must identify different resources",
    ):
        ResourceRelationship(
            source=source_uuid,
            target=source_uuid,
            relationship_type=RelationshipType.RELATED_TO,
        )


def test_invalid_source_type_is_rejected(
    target_uuid: ResourceUUID,
) -> None:
    with pytest.raises(TypeError, match="source must be a ResourceUUID"):
        ResourceRelationship(
            source="source",  # type: ignore[arg-type]
            target=target_uuid,
            relationship_type=RelationshipType.CITES,
        )


def test_invalid_target_type_is_rejected(
    source_uuid: ResourceUUID,
) -> None:
    with pytest.raises(TypeError, match="target must be a ResourceUUID"):
        ResourceRelationship(
            source=source_uuid,
            target="target",  # type: ignore[arg-type]
            relationship_type=RelationshipType.CITES,
        )


def test_invalid_relationship_type_is_rejected(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    with pytest.raises(
        TypeError,
        match="relationship_type must be a RelationshipType",
    ):
        ResourceRelationship(
            source=source_uuid,
            target=target_uuid,
            relationship_type="AMENDS",  # type: ignore[arg-type]
        )


def test_invalid_validity_type_is_rejected(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    with pytest.raises(
        TypeError,
        match="validity must be a ValidityPeriod",
    ):
        ResourceRelationship(
            source=source_uuid,
            target=target_uuid,
            relationship_type=RelationshipType.AMENDS,
            validity="always",  # type: ignore[arg-type]
        )


def test_connects_reports_source_and_target(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    assert relationship.connects(source_uuid)
    assert relationship.connects(target_uuid)
    assert not relationship.connects(ResourceUUID.generate())


def test_originates_from_reports_direction(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    assert relationship.originates_from(source_uuid)
    assert not relationship.originates_from(target_uuid)


def test_points_to_reports_direction(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    assert relationship.points_to(target_uuid)
    assert not relationship.points_to(source_uuid)


def test_identity_methods_reject_invalid_type(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    with pytest.raises(TypeError, match="resource_uuid must be a ResourceUUID"):
        relationship.connects("invalid")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="resource_uuid must be a ResourceUUID"):
        relationship.originates_from("invalid")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="resource_uuid must be a ResourceUUID"):
        relationship.points_to("invalid")  # type: ignore[arg-type]


def test_is_active_on_uses_relationship_validity(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.AMENDS,
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    assert relationship.is_active_on(date(2024, 1, 1))
    assert relationship.is_active_on(date(2024, 6, 1))
    assert relationship.is_active_on(date(2024, 12, 31))
    assert not relationship.is_active_on(date(2025, 1, 1))


def test_is_active_on_rejects_invalid_type(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    with pytest.raises(TypeError, match="value must be a date"):
        relationship.is_active_on("2024-01-01")  # type: ignore[arg-type]


def test_relationship_is_immutable(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    relationship = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    with pytest.raises(FrozenInstanceError):
        relationship.target = ResourceUUID.generate()  # type: ignore[misc]


def test_relationship_is_hashable_and_comparable(
    source_uuid: ResourceUUID,
    target_uuid: ResourceUUID,
) -> None:
    first = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )
    second = ResourceRelationship(
        source=source_uuid,
        target=target_uuid,
        relationship_type=RelationshipType.CITES,
    )

    assert first == second
    assert hash(first) == hash(second)
    assert {first, second} == {first}
