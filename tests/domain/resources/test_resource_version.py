"""Tests for the ResourceVersion business concept."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from eke.domain.identity import ResourceUUID, ResourceVersionUUID
from eke.domain.resources import ResourceStatus, ResourceVersion
from eke.domain.temporal import ValidityPeriod


@pytest.fixture
def resource_uuid() -> ResourceUUID:
    return ResourceUUID.generate()


@pytest.fixture
def version_uuid() -> ResourceVersionUUID:
    return ResourceVersionUUID.generate()


def test_create_resource_version(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )

    assert version.version_uuid == version_uuid
    assert version.resource_uuid == resource_uuid
    assert version.status is ResourceStatus.IN_FORCE
    assert version.validity == ValidityPeriod()
    assert version.previous_version_uuid is None


def test_previous_version_reference_is_supported(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    previous = ResourceVersionUUID.generate()

    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
        previous_version_uuid=previous,
    )

    assert version.has_previous_version
    assert version.previous_version_uuid == previous


def test_self_previous_version_reference_is_rejected(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    with pytest.raises(
        ValueError,
        match="cannot reference itself",
    ):
        ResourceVersion(
            version_uuid=version_uuid,
            resource_uuid=resource_uuid,
            status=ResourceStatus.IN_FORCE,
            previous_version_uuid=version_uuid,
        )


@pytest.mark.parametrize(
    ("field_name", "value", "expected_message"),
    [
        (
            "version_uuid",
            "invalid",
            "version_uuid must be a ResourceVersionUUID",
        ),
        (
            "resource_uuid",
            "invalid",
            "resource_uuid must be a ResourceUUID",
        ),
        (
            "status",
            "IN_FORCE",
            "status must be a ResourceStatus",
        ),
        (
            "validity",
            "always",
            "validity must be a ValidityPeriod",
        ),
        (
            "previous_version_uuid",
            "invalid",
            "previous_version_uuid must be a ResourceVersionUUID or None",
        ),
    ],
)
def test_invalid_field_types_are_rejected(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
    field_name: str,
    value: object,
    expected_message: str,
) -> None:
    arguments: dict[str, object] = {
        "version_uuid": version_uuid,
        "resource_uuid": resource_uuid,
        "status": ResourceStatus.IN_FORCE,
        "validity": ValidityPeriod(),
        "previous_version_uuid": None,
    }
    arguments[field_name] = value

    with pytest.raises(TypeError, match=expected_message):
        ResourceVersion(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (ResourceStatus.IN_FORCE, True),
        (ResourceStatus.PARTIALLY_IN_FORCE, True),
        (ResourceStatus.PUBLISHED, False),
        (ResourceStatus.REPEALED, False),
    ],
)
def test_is_effective_delegates_to_status(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
    status: ResourceStatus,
    expected: bool,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=status,
    )

    assert version.is_effective is expected


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (ResourceStatus.REPEALED, True),
        (ResourceStatus.EXPIRED, True),
        (ResourceStatus.SUPERSEDED, True),
        (ResourceStatus.IN_FORCE, False),
    ],
)
def test_is_terminal_delegates_to_status(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
    status: ResourceStatus,
    expected: bool,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=status,
    )

    assert version.is_terminal is expected


def test_belongs_to_reports_resource_ownership(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.PUBLISHED,
    )

    assert version.belongs_to(resource_uuid)
    assert not version.belongs_to(ResourceUUID.generate())


def test_belongs_to_rejects_invalid_type(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.PUBLISHED,
    )

    with pytest.raises(
        TypeError,
        match="resource_uuid must be a ResourceUUID",
    ):
        version.belongs_to("invalid")  # type: ignore[arg-type]


def test_is_valid_on_uses_validity_period(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    assert version.is_valid_on(date(2024, 1, 1))
    assert version.is_valid_on(date(2024, 12, 31))
    assert not version.is_valid_on(date(2025, 1, 1))


def test_succeeds_returns_true_for_direct_predecessor(
    resource_uuid: ResourceUUID,
) -> None:
    previous = ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=resource_uuid,
        status=ResourceStatus.SUPERSEDED,
    )
    current = ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
        previous_version_uuid=previous.version_uuid,
    )

    assert current.succeeds(previous)


def test_succeeds_returns_false_for_different_resource() -> None:
    previous = ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=ResourceUUID.generate(),
        status=ResourceStatus.SUPERSEDED,
    )
    current = ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=ResourceUUID.generate(),
        status=ResourceStatus.IN_FORCE,
        previous_version_uuid=previous.version_uuid,
    )

    assert not current.succeeds(previous)


def test_succeeds_rejects_invalid_type(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    version = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )

    with pytest.raises(TypeError, match="other must be a ResourceVersion"):
        version.succeeds("invalid")  # type: ignore[arg-type]


def test_resource_version_is_immutable_hashable_and_comparable(
    resource_uuid: ResourceUUID,
    version_uuid: ResourceVersionUUID,
) -> None:
    first = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )
    second = ResourceVersion(
        version_uuid=version_uuid,
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )

    assert first == second
    assert hash(first) == hash(second)

    with pytest.raises(FrozenInstanceError):
        first.status = ResourceStatus.REPEALED  # type: ignore[misc]
