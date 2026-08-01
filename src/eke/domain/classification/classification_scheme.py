"""Classification scheme enumeration.

This module defines the canonical vocabulary used to identify supported
classification systems.
"""

from __future__ import annotations

from enum import StrEnum


class ClassificationScheme(StrEnum):
    """Represent the classification system of a concept."""

    EUROVOC = "EUROVOC"
    DIRECTORY_CODE = "DIRECTORY_CODE"
    SUBJECT_MATTER = "SUBJECT_MATTER"
    LEGAL_DOMAIN = "LEGAL_DOMAIN"
    POLICY_AREA = "POLICY_AREA"
    INTERNAL = "INTERNAL"
    OTHER = "OTHER"
