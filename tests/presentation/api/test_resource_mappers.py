"""Tests for Resource HTTP/domain mappers."""

from __future__ import annotations

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import Resource, ResourceStatus
from eke.presentation.api.mappers import (
    resource_from_create,
    resource_from_update,
    resource_to_response,
)
from eke.presentation.api.schemas import (
    BusinessIdentifierSchema,
    ResourceCreateRequest,
    ResourceUpdateRequest,
)


def test_create_mapper_builds_resource() -> None:
    request = ResourceCreateRequest(
        identifiers=[
            BusinessIdentifierSchema(
                scheme=IdentifierScheme.CELEX,
                value="32023R1114",
            )
        ]
    )

    resource = resource_from_create(request)

    assert isinstance(resource.resource_uuid, ResourceUUID)
    assert resource.identifiers[0] == BusinessIdentifier(
        IdentifierScheme.CELEX,
        "32023R1114",
    )


def test_update_mapper_preserves_rich_collections() -> None:
    existing = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )
    request = ResourceUpdateRequest(
        identifiers=[
            BusinessIdentifierSchema(
                scheme=IdentifierScheme.CELEX,
                value="32013R0575",
            )
        ],
        resource_type=existing.resource_type,
        status=ResourceStatus.IN_FORCE,
    )

    updated = resource_from_update(existing, request)

    assert updated.resource_uuid == existing.resource_uuid
    assert updated.titles == existing.titles
    assert updated.versions == existing.versions
    assert updated.relationships == existing.relationships
    assert updated.provenance_records == (
        existing.provenance_records
    )
    assert updated.classifications == (
        existing.classifications
    )


def test_response_mapper_serializes_core_fields() -> None:
    resource = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )

    response = resource_to_response(resource)

    assert response.resource_uuid == str(
        resource.resource_uuid
    )
    assert response.identifiers[0].value == "32023R1114"
