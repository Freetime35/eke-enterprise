from __future__ import annotations

from dataclasses import dataclass

from eke.domain.identity.identifier_scheme import IdentifierScheme


@dataclass(frozen=True, slots=True)
class BusinessIdentifier:
    """Immutable external business identifier."""

    scheme: IdentifierScheme
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.scheme, IdentifierScheme):
            raise TypeError("scheme must be an IdentifierScheme")
        if not isinstance(self.value, str):
            raise TypeError("value must be a string")
        if not self.value.strip():
            raise ValueError("value must not be empty")
