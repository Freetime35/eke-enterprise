from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from eke.domain.identity import BusinessIdentifier, IdentifierScheme


def test_create_business_identifier() -> None:
    identifier = BusinessIdentifier(
        scheme=IdentifierScheme.CELEX,
        value="32023R1114",
    )
    assert identifier.scheme is IdentifierScheme.CELEX
    assert identifier.value == "32023R1114"


def test_empty_value_rejected() -> None:
    with pytest.raises(ValueError):
        BusinessIdentifier(IdentifierScheme.CELEX, "")


def test_non_string_value_rejected() -> None:
    with pytest.raises(TypeError):
        BusinessIdentifier(IdentifierScheme.CELEX, 123)  # type: ignore[arg-type]


def test_non_scheme_rejected() -> None:
    with pytest.raises(TypeError):
        BusinessIdentifier("CELEX", "32023R1114")  # type: ignore[arg-type]


def test_is_immutable() -> None:
    identifier = BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114")
    with pytest.raises(FrozenInstanceError):
        identifier.value = "x"  # type: ignore[misc]


def test_hashable_and_equal() -> None:
    a = BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114")
    b = BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114")
    assert a == b
    assert hash(a) == hash(b)
