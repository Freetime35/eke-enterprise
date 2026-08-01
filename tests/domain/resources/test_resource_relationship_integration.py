"""Tests for Resource relationship aggregate integration."""

from __future__ import annotations

from datetime import date

import pytest

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.relationships import (
    RelationshipType,
    ResourceRelationship,
)
from eke.domain.resources import Resource
from eke.domain.temporal import ValidityPeriod


def make_identifier() -> BusinessIdentifier:
    return BusinessIdentifier(
        IdentifierScheme.CELEX,
        "32023R1114",
    )


def make_resource(
    resource_uuid: ResourceUUID,
    relationships: tuple[ResourceRelationship, ...] = (),
) -> Resource:
    return Resource(
        resource_uuid=resource_uuid,
        identifiers=(make_identifier(),),
        relationships=relationships,
    )


def test_default_relationship_collection_is_empty() -> None:
    resource = make_resource(ResourceUUID.generate())

    assert resource.relationships == ()


def test_resource_accepts_outgoing_relationships() -> None:
    source = ResourceUUID.generate()
    target = ResourceUUID.generate()
    relationship = ResourceRelationship(
        source=source,
        target=target,
        relationship_type=RelationshipType.AMENDS,
    )

    resource = make_resource(source, (relationship,))

    assert resource.relationships == (relationship,)


def test_relationships_must_be_a_tuple() -> None:
    with pytest.raises(TypeError, match="relationships must be a tuple"):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(make_identifier(),),
            relationships=[],  # type: ignore[arg-type]
        )


def test_relationship_collection_rejects_invalid_members() -> None:
    with pytest.raises(
        TypeError,
        match="only ResourceRelationship instances",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(make_identifier(),),
            relationships=("AMENDS",),  # type: ignore[arg-type]
        )


def test_duplicate_relationships_are_rejected() -> None:
    source = ResourceUUID.generate()
    relationship = ResourceRelationship(
        source=source,
        target=ResourceUUID.generate(),
        relationship_type=RelationshipType.CITES,
    )

    with pytest.raises(
        ValueError,
        match="resource relationships must be unique",
    ):
        make_resource(source, (relationship, relationship))


def test_incoming_relationship_is_rejected() -> None:
    aggregate_uuid = ResourceUUID.generate()
    relationship = ResourceRelationship(
        source=ResourceUUID.generate(),
        target=aggregate_uuid,
        relationship_type=RelationshipType.AMENDED_BY,
    )

    with pytest.raises(
        ValueError,
        match="must originate from the resource",
    ):
        make_resource(aggregate_uuid, (relationship,))


def test_relationships_of_type_filters_relationships() -> None:
    source = ResourceUUID.generate()
    amends = ResourceRelationship(
        source=source,
        target=ResourceUUID.generate(),
        relationship_type=RelationshipType.AMENDS,
    )
    cites = ResourceRelationship(
        source=source,
        target=ResourceUUID.generate(),
        relationship_type=RelationshipType.CITES,
    )
    resource = make_resource(source, (amends, cites))

    assert resource.relationships_of_type(
        RelationshipType.AMENDS
    ) == (amends,)
    assert resource.relationships_of_type(
        RelationshipType.REPEALS
    ) == ()


def test_relationships_of_type_rejects_invalid_type() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        TypeError,
        match="relationship_type must be a RelationshipType",
    ):
        resource.relationships_of_type(  # type: ignore[arg-type]
            "AMENDS"
        )


def test_relationships_to_filters_by_target() -> None:
    source = ResourceUUID.generate()
    target = ResourceUUID.generate()
    other_target = ResourceUUID.generate()
    first = ResourceRelationship(
        source=source,
        target=target,
        relationship_type=RelationshipType.AMENDS,
    )
    second = ResourceRelationship(
        source=source,
        target=other_target,
        relationship_type=RelationshipType.CITES,
    )
    resource = make_resource(source, (first, second))

    assert resource.relationships_to(target) == (first,)
    assert resource.relationships_to(
        ResourceUUID.generate()
    ) == ()


def test_relationships_to_rejects_invalid_target() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        TypeError,
        match="target must be a ResourceUUID",
    ):
        resource.relationships_to("target")  # type: ignore[arg-type]


def test_active_relationships_on_filters_by_validity() -> None:
    source = ResourceUUID.generate()
    historic = ResourceRelationship(
        source=source,
        target=ResourceUUID.generate(),
        relationship_type=RelationshipType.CITES,
        validity=ValidityPeriod(
            valid_from=date(2020, 1, 1),
            valid_to=date(2023, 12, 31),
        ),
    )
    current = ResourceRelationship(
        source=source,
        target=ResourceUUID.generate(),
        relationship_type=RelationshipType.AMENDS,
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
        ),
    )
    resource = make_resource(source, (historic, current))

    assert resource.active_relationships_on(
        date(2022, 1, 1)
    ) == (historic,)
    assert resource.active_relationships_on(
        date(2025, 1, 1)
    ) == (current,)


def test_active_relationships_on_rejects_invalid_date() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(TypeError, match="value must be a date"):
        resource.active_relationships_on(  # type: ignore[arg-type]
            "today"
        )


def test_multiple_distinct_relationships_to_same_target_are_allowed() -> None:
    source = ResourceUUID.generate()
    target = ResourceUUID.generate()
    first = ResourceRelationship(
        source=source,
        target=target,
        relationship_type=RelationshipType.CITES,
    )
    second = ResourceRelationship(
        source=source,
        target=target,
        relationship_type=RelationshipType.AMENDS,
    )

    resource = make_resource(source, (first, second))

    assert resource.relationships_to(target) == (first, second)
