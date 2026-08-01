"""Resource title business concept.

This module defines a language-specific resource title with an optional
temporal validity period.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.temporal import ValidityPeriod


@dataclass(frozen=True, slots=True)
class ResourceTitle:
    """Represent a localized title valid during a temporal period.

    Attributes:
        text: Localized title text.
        validity: Inclusive temporal validity of the title.
    """

    text: LocalizedText
    validity: ValidityPeriod = ValidityPeriod()

    def __post_init__(self) -> None:
        """Validate business concept invariants."""
        if not isinstance(self.text, LocalizedText):
            raise TypeError("text must be a LocalizedText")

        if not isinstance(self.validity, ValidityPeriod):
            raise TypeError("validity must be a ValidityPeriod")

    @property
    def language(self) -> LanguageCode:
        """Return the title language."""
        return self.text.language

    @property
    def value(self) -> str:
        """Return the title text value."""
        return self.text.value

    @property
    def is_open_ended(self) -> bool:
        """Return whether the title has no upper validity boundary."""
        return self.validity.is_open_end

    def is_valid_on(self, value: date) -> bool:
        """Return whether the title is valid on a date.

        Args:
            value: Date to evaluate.

        Returns:
            True when the title is valid on the requested date.

        Raises:
            TypeError: If value is not a date.
        """
        return self.validity.contains(value)

    def has_language(self, language: LanguageCode) -> bool:
        """Return whether the title uses the requested language.

        Args:
            language: Language code to compare.

        Returns:
            True when the title language matches.

        Raises:
            TypeError: If language is not a LanguageCode.
        """
        return self.text.is_language(language)

    def overlaps(self, other: ResourceTitle) -> bool:
        """Return whether two titles overlap in the same language.

        Titles in different languages do not conflict and therefore do
        not overlap from the domain perspective.

        Args:
            other: Resource title to compare.

        Returns:
            True when both titles use the same language and their
            validity periods overlap.

        Raises:
            TypeError: If other is not a ResourceTitle.
        """
        if not isinstance(other, ResourceTitle):
            raise TypeError("other must be a ResourceTitle")

        return (
            self.language == other.language
            and self.validity.overlaps(other.validity)
        )
