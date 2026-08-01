"""Tests for the ResourceStatus enumeration."""

from __future__ import annotations

import pytest

from eke.domain.resources import ResourceStatus


def test_supported_resource_statuses_are_defined() -> None:
    assert tuple(ResourceStatus) == (
        ResourceStatus.DRAFT,
        ResourceStatus.ADOPTED,
        ResourceStatus.PUBLISHED,
        ResourceStatus.IN_FORCE,
        ResourceStatus.PARTIALLY_IN_FORCE,
        ResourceStatus.NOT_YET_IN_FORCE,
        ResourceStatus.REPEALED,
        ResourceStatus.EXPIRED,
        ResourceStatus.WITHDRAWN,
        ResourceStatus.ANNULLED,
        ResourceStatus.SUPERSEDED,
        ResourceStatus.UNKNOWN,
    )


@pytest.mark.parametrize(
    "status",
    list(ResourceStatus),
)
def test_resource_status_serializes_to_stable_string(
    status: ResourceStatus,
) -> None:
    assert str(status) == status.value


def test_resource_status_can_be_created_from_valid_string() -> None:
    assert ResourceStatus("IN_FORCE") is ResourceStatus.IN_FORCE


def test_resource_status_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        ResourceStatus("INVALID")


def test_resource_status_members_are_unique() -> None:
    values = [status.value for status in ResourceStatus]

    assert len(values) == len(set(values))


@pytest.mark.parametrize(
    "status",
    [
        ResourceStatus.REPEALED,
        ResourceStatus.EXPIRED,
        ResourceStatus.WITHDRAWN,
        ResourceStatus.ANNULLED,
        ResourceStatus.SUPERSEDED,
    ],
)
def test_terminal_statuses_are_reported(status: ResourceStatus) -> None:
    assert status.is_terminal


@pytest.mark.parametrize(
    "status",
    [
        ResourceStatus.DRAFT,
        ResourceStatus.ADOPTED,
        ResourceStatus.PUBLISHED,
        ResourceStatus.IN_FORCE,
        ResourceStatus.PARTIALLY_IN_FORCE,
        ResourceStatus.NOT_YET_IN_FORCE,
        ResourceStatus.UNKNOWN,
    ],
)
def test_non_terminal_statuses_are_reported(status: ResourceStatus) -> None:
    assert not status.is_terminal


@pytest.mark.parametrize(
    "status",
    [
        ResourceStatus.IN_FORCE,
        ResourceStatus.PARTIALLY_IN_FORCE,
    ],
)
def test_effective_statuses_are_reported(status: ResourceStatus) -> None:
    assert status.is_effective


@pytest.mark.parametrize(
    "status",
    [
        ResourceStatus.DRAFT,
        ResourceStatus.ADOPTED,
        ResourceStatus.PUBLISHED,
        ResourceStatus.NOT_YET_IN_FORCE,
        ResourceStatus.REPEALED,
        ResourceStatus.EXPIRED,
        ResourceStatus.WITHDRAWN,
        ResourceStatus.ANNULLED,
        ResourceStatus.SUPERSEDED,
        ResourceStatus.UNKNOWN,
    ],
)
def test_non_effective_statuses_are_reported(status: ResourceStatus) -> None:
    assert not status.is_effective


@pytest.mark.parametrize(
    "status",
    [
        ResourceStatus.DRAFT,
        ResourceStatus.ADOPTED,
        ResourceStatus.PUBLISHED,
        ResourceStatus.NOT_YET_IN_FORCE,
    ],
)
def test_pre_effective_statuses_are_reported(status: ResourceStatus) -> None:
    assert status.is_pre_effective


@pytest.mark.parametrize(
    "status",
    [
        ResourceStatus.IN_FORCE,
        ResourceStatus.PARTIALLY_IN_FORCE,
        ResourceStatus.REPEALED,
        ResourceStatus.EXPIRED,
        ResourceStatus.WITHDRAWN,
        ResourceStatus.ANNULLED,
        ResourceStatus.SUPERSEDED,
        ResourceStatus.UNKNOWN,
    ],
)
def test_non_pre_effective_statuses_are_reported(
    status: ResourceStatus,
) -> None:
    assert not status.is_pre_effective
