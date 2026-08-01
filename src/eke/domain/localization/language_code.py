"""Language code value object.

This module defines the canonical language code representation used by
EKE Enterprise.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LanguageCode:
    """Represent a canonical ISO 639-1 language code.

    Language codes are stored in lowercase canonical form.

    Attributes:
        value: Two-letter ISO 639-1 language code.
    """

    value: str

    def __post_init__(self) -> None:
        """Validate and normalize the language code."""
        if not isinstance(self.value, str):
            raise TypeError("value must be a string")

        normalized = self.value.strip().lower()

        if len(normalized) != 2 or not normalized.isascii() or not normalized.isalpha():
            raise ValueError(
                "value must be a two-letter ASCII language code"
            )

        object.__setattr__(self, "value", normalized)

    @classmethod
    def from_string(cls, value: str) -> LanguageCode:
        """Create a language code from text.

        Args:
            value: Language code text.

        Returns:
            A normalized LanguageCode instance.
        """
        return cls(value)

    def __str__(self) -> str:
        """Return the canonical lowercase language code."""
        return self.value

    def __repr__(self) -> str:
        """Return an unambiguous developer representation."""
        return f"{self.__class__.__name__}('{self.value}')"

    def to_uppercase(self) -> str:
        """Return the uppercase representation used by some source systems."""
        return self.value.upper()
