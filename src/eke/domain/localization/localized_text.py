"""Localized text value object.

This module defines immutable text associated with a canonical
language code.
"""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.localization.language_code import LanguageCode


@dataclass(frozen=True, slots=True)
class LocalizedText:
    """Represent immutable text expressed in one language.

    The text value is preserved exactly as provided, while empty or
    whitespace-only values are rejected.

    Attributes:
        language: Canonical language code of the text.
        value: Localized text content.
    """

    language: LanguageCode
    value: str

    def __post_init__(self) -> None:
        """Validate value object invariants."""
        if not isinstance(self.language, LanguageCode):
            raise TypeError("language must be a LanguageCode")

        if not isinstance(self.value, str):
            raise TypeError("value must be a string")

        if not self.value.strip():
            raise ValueError("value must not be empty")

    def __str__(self) -> str:
        """Return the localized text content."""
        return self.value

    def __repr__(self) -> str:
        """Return an unambiguous developer representation."""
        return (
            f"{self.__class__.__name__}("
            f"language={self.language!r}, value={self.value!r})"
        )

    def is_language(self, language: LanguageCode) -> bool:
        """Return whether the text uses the requested language.

        Args:
            language: Language code to compare.

        Returns:
            True when the text language matches the requested language.

        Raises:
            TypeError: If language is not a LanguageCode.
        """
        if not isinstance(language, LanguageCode):
            raise TypeError("language must be a LanguageCode")

        return self.language == language
