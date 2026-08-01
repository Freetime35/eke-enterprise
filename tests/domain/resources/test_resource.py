"""Tests for the Resource aggregate root."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import Resource


@pytest.fixture
def celex_identifier() -> BusinessIdentifier:
    return BusinessIdentifier(
        scheme=IdentifierScheme.CELEX,
        value="32023R1114",
    )


@pytest.fixture
def eli_identifier() -> BusinessIdentifier:
    return BusinessIdentifier(
        scheme=IdentifierScheme.ELI,
        value="http://data.europa.eu/eli/reg/2023/1114/oj",
    )


def test_create_resource_with_one_identifier(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource_uuid = ResourceUUID.generate()

    resource = Resource(
        resource_uuid=resource_uuid,
        identifiers=(celex_identifier,),
    )

    assert resource.resource_uuid == resource_uuid
    assert resource.identifiers == (celex_identifier,)


def test_create_resource_with_multiple_identifier_schemes(
    celex_identifier: BusinessIdentifier,
    eli_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier, eli_identifier),
    )

    assert resource.has_identifier(celex_identifier)
    assert resource.has_identifier(eli_identifier)


def test_resource_requires_resource_uuid(
    celex_identifier: BusinessIdentifier,
) -> None:
    with pytest.raises(
        TypeError,
        match="resource_uuid must be a ResourceUUID",
    ):
        Resource(
            resource_uuid="invalid",  # type: ignore[arg-type]
            identifiers=(celex_identifier,),
        )


def test_resource_requires_identifier_tuple(
    celex_identifier: BusinessIdentifier,
) -> None:
    with pytest.raises(TypeError, match="identifiers must be a tuple"):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=[celex_identifier],  # type: ignore[arg-type]
        )


def test_resource_requires_at_least_one_identifier() -> None:
    with pytest.raises(
        ValueError,
        match="at least one business identifier",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(),
        )


def test_resource_rejects_non_business_identifier() -> None:
    with pytest.raises(
        TypeError,
        match="only BusinessIdentifier instances",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=("32023R1114",),  # type: ignore[arg-type]
        )


def test_resource_rejects_duplicate_identifiers(
    celex_identifier: BusinessIdentifier,
) -> None:
    with pytest.raises(
        ValueError,
        match="business identifiers must be unique",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(celex_identifier, celex_identifier),
        )


def test_resource_rejects_multiple_identifiers_for_same_scheme() -> None:
    first = BusinessIdentifier(
        scheme=IdentifierScheme.CELEX,
        value="32023R1114",
    )
    second = BusinessIdentifier(
        scheme=IdentifierScheme.CELEX,
        value="32013R0575",
    )

    with pytest.raises(
        ValueError,
        match="multiple identifiers for the same scheme",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(first, second),
        )


def test_find_identifier_returns_matching_identifier(
    celex_identifier: BusinessIdentifier,
    eli_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier, eli_identifier),
    )

    assert resource.find_identifier(IdentifierScheme.CELEX) == celex_identifier
    assert resource.find_identifier(IdentifierScheme.ELI) == eli_identifier


def test_find_identifier_returns_none_for_missing_scheme(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier,),
    )

    assert resource.find_identifier(IdentifierScheme.CELLAR) is None


def test_has_identifier_scheme_reports_presence(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier,),
    )

    assert resource.has_identifier_scheme(IdentifierScheme.CELEX)
    assert not resource.has_identifier_scheme(IdentifierScheme.ELI)


def test_has_identifier_rejects_invalid_type(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier,),
    )

    with pytest.raises(
        TypeError,
        match="identifier must be a BusinessIdentifier",
    ):
        resource.has_identifier("32023R1114")  # type: ignore[arg-type]


def test_find_identifier_rejects_invalid_scheme(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier,),
    )

    with pytest.raises(
        TypeError,
        match="scheme must be an IdentifierScheme",
    ):
        resource.find_identifier("CELEX")  # type: ignore[arg-type]


def test_resource_is_immutable(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource = Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(celex_identifier,),
    )

    with pytest.raises(FrozenInstanceError):
        resource.identifiers = ()  # type: ignore[misc]


def test_resource_is_hashable(
    celex_identifier: BusinessIdentifier,
) -> None:
    resource_uuid = ResourceUUID.generate()
    first = Resource(
        resource_uuid=resource_uuid,
        identifiers=(celex_identifier,),
    )
    second = Resource(
        resource_uuid=resource_uuid,
        identifiers=(celex_identifier,),
    )

    assert first == second
    assert hash(first) == hash(second)
