"""Classification concept business value object.

This module defines a canonical concept from a classification scheme,
with a stable code, localized label, and temporal validity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.domain.classification.classification_scheme import (
    ClassificationScheme,
)
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.temporal import ValidityPeriod


@dataclass(frozen=True, slots=True)
class ClassificationConcept:
    """Represent a canonical classification concept.

    Attributes:
        scheme: Classification system owning the concept.
        code: Stable source-independent or source-preserved code.
        label: Localized human-readable label.
        validity: Inclusive temporal validity of the concept.
    """

    scheme: ClassificationScheme
    code: str
    label: LocalizedText
    validity: ValidityPeriod = ValidityPeriod()

    def __post_init__(self) -> None:
        """Validate concept invariants."""
        if not isinstance(self.scheme, ClassificationScheme):
            raise TypeError(
                "scheme must be a ClassificationScheme"
            )

        if not isinstance(self.code, str):
            raise TypeError("code must be a string")

        if not self.code.strip():
            raise ValueError("code must not be empty")

        if not isinstance(self.label, LocalizedText):
            raise TypeError("label must be a LocalizedText")

        if not isinstance(self.validity, ValidityPeriod):
            raise TypeError("validity must be a ValidityPeriod")

    @property
    def language(self) -> LanguageCode:
        """Return the label language."""
        return self.label.language

    @property
    def label_value(self) -> str:
        """Return the localized label value."""
        return self.label.value

    def has_code(self, code: str) -> bool:
        """Return whether the concept uses the supplied code."""
        if not isinstance(code, str):
            raise TypeError("code must be a string")

        return self.code == code

    def belongs_to_scheme(
        self,
        scheme: ClassificationScheme,
    ) -> bool:
        """Return whether the concept belongs to a scheme."""
        if not isinstance(scheme, ClassificationScheme):
            raise TypeError(
                "scheme must be a ClassificationScheme"
            )

        return self.scheme is scheme

    def has_language(self, language: LanguageCode) -> bool:
        """Return whether the label uses the requested language."""
        return self.label.is_language(language)

    def is_valid_on(self, value: date) -> bool:
        """Return whether the concept is valid on a date."""
        return self.validity.contains(value)
