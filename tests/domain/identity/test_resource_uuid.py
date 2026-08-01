"""Tests for the ResourceUUID value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from eke.domain.identity import ResourceUUID


def test_generate_returns_resource_uuid() -> None:
    identifier = ResourceUUID.generate()

    assert isinstance(identifier, ResourceUUID)
    assert isinstance(identifier.value, UUID)
    assert identifier.value.version == 4


def test_generate_returns_unique_values() -> None:
    first = ResourceUUID.generate()
    second = ResourceUUID.generate()

    assert first != second


def test_from_string_parses_canonical_uuid() -> None:
    raw = "550e8400-e29b-41d4-a716-446655440000"

    identifier = ResourceUUID.from_string(raw)

    assert identifier.value == UUID(raw)
    assert str(identifier) == raw


def test_from_string_accepts_uppercase_uuid() -> None:
    raw = "550E8400-E29B-41D4-A716-446655440000"

    identifier = ResourceUUID.from_string(raw)

    assert str(identifier) == raw.lower()


def test_from_string_rejects_invalid_uuid() -> None:
    with pytest.raises(ValueError):
        ResourceUUID.from_string("not-a-valid-uuid")


def test_from_string_rejects_non_string_value() -> None:
    with pytest.raises(TypeError, match="value must be a string"):
        ResourceUUID.from_string(123)  # type: ignore[arg-type]


def test_constructor_rejects_non_uuid_value() -> None:
    with pytest.raises(TypeError, match="value must be an instance of uuid.UUID"):
        ResourceUUID("invalid")  # type: ignore[arg-type]


def test_value_object_is_immutable() -> None:
    identifier = ResourceUUID.generate()

    with pytest.raises(FrozenInstanceError):
        identifier.value = UUID(int=0)  # type: ignore[misc]


def test_equal_values_are_equal_and_hashable() -> None:
    raw = UUID("550e8400-e29b-41d4-a716-446655440000")
    first = ResourceUUID(raw)
    second = ResourceUUID(raw)

    assert first == second
    assert hash(first) == hash(second)
    assert {first, second} == {first}


def test_repr_is_unambiguous() -> None:
    raw = "550e8400-e29b-41d4-a716-446655440000"
    identifier = ResourceUUID.from_string(raw)

    assert repr(identifier) == f"ResourceUUID('{raw}')"
