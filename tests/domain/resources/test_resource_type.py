"""Tests for the ResourceType enumeration."""

from __future__ import annotations

import pytest

from eke.domain.resources import ResourceType


def test_supported_resource_types_are_defined() -> None:
    assert tuple(ResourceType) == (
        ResourceType.REGULATION,
        ResourceType.DIRECTIVE,
        ResourceType.DECISION,
        ResourceType.RECOMMENDATION,
        ResourceType.OPINION,
        ResourceType.TREATY,
        ResourceType.CASE_LAW,
        ResourceType.NOTICE,
        ResourceType.COMMUNICATION,
        ResourceType.GUIDELINE,
        ResourceType.REPORT,
        ResourceType.PROPOSAL,
        ResourceType.CORRIGENDUM,
        ResourceType.OTHER,
    )


@pytest.mark.parametrize(
    ("resource_type", "expected"),
    [
        (ResourceType.REGULATION, "REGULATION"),
        (ResourceType.DIRECTIVE, "DIRECTIVE"),
        (ResourceType.DECISION, "DECISION"),
        (ResourceType.RECOMMENDATION, "RECOMMENDATION"),
        (ResourceType.OPINION, "OPINION"),
        (ResourceType.TREATY, "TREATY"),
        (ResourceType.CASE_LAW, "CASE_LAW"),
        (ResourceType.NOTICE, "NOTICE"),
        (ResourceType.COMMUNICATION, "COMMUNICATION"),
        (ResourceType.GUIDELINE, "GUIDELINE"),
        (ResourceType.REPORT, "REPORT"),
        (ResourceType.PROPOSAL, "PROPOSAL"),
        (ResourceType.CORRIGENDUM, "CORRIGENDUM"),
        (ResourceType.OTHER, "OTHER"),
    ],
)
def test_resource_type_serializes_to_stable_string(
    resource_type: ResourceType,
    expected: str,
) -> None:
    assert resource_type.value == expected
    assert str(resource_type) == expected


def test_resource_type_can_be_created_from_valid_string() -> None:
    assert ResourceType("REGULATION") is ResourceType.REGULATION


def test_resource_type_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        ResourceType("UNKNOWN")


def test_resource_type_behaves_like_string() -> None:
    assert ResourceType.DIRECTIVE == "DIRECTIVE"
    assert ResourceType.CASE_LAW.lower() == "case_law"


def test_resource_type_members_are_unique() -> None:
    values = [resource_type.value for resource_type in ResourceType]

    assert len(values) == len(set(values))
