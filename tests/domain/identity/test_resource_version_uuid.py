"""Tests for the ResourceVersionUUID value object."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from eke.domain.identity import ResourceVersionUUID


def test_generate_returns_version_uuid() -> None:
    identifier = ResourceVersionUUID.generate()

    assert isinstance(identifier, ResourceVersionUUID)
    assert isinstance(identifier.value, UUID)
    assert identifier.value.version == 4


def test_generate_returns_unique_values() -> None:
    assert ResourceVersionUUID.generate() != ResourceVersionUUID.generate()


def test_from_string_roundtrip() -> None:
    raw = "550e8400-e29b-41d4-a716-446655440000"

    identifier = ResourceVersionUUID.from_string(raw)

    assert str(identifier) == raw


def test_from_string_rejects_invalid_uuid() -> None:
    with pytest.raises(ValueError):
        ResourceVersionUUID.from_string("invalid")


def test_from_string_rejects_non_string() -> None:
    with pytest.raises(TypeError, match="value must be a string"):
        ResourceVersionUUID.from_string(123)  # type: ignore[arg-type]


def test_constructor_rejects_non_uuid() -> None:
    with pytest.raises(
        TypeError,
        match="value must be an instance of uuid.UUID",
    ):
        ResourceVersionUUID("invalid")  # type: ignore[arg-type]


def test_version_uuid_is_immutable_hashable_and_comparable() -> None:
    value = UUID("550e8400-e29b-41d4-a716-446655440000")
    first = ResourceVersionUUID(value)
    second = ResourceVersionUUID(value)

    assert first == second
    assert hash(first) == hash(second)

    with pytest.raises(FrozenInstanceError):
        first.value = UUID(int=0)  # type: ignore[misc]


def test_repr_is_unambiguous() -> None:
    raw = "550e8400-e29b-41d4-a716-446655440000"

    assert repr(ResourceVersionUUID.from_string(raw)) == (
        f"ResourceVersionUUID('{raw}')"
    )
