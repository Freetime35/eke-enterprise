"""Resource relationship type enumeration.

This module defines the canonical vocabulary used to describe directed
relationships between resources.
"""

from __future__ import annotations

from enum import StrEnum


class RelationshipType(StrEnum):
    """Represent a canonical directed relationship between resources."""

    CITES = "CITES"
    AMENDS = "AMENDS"
    AMENDED_BY = "AMENDED_BY"
    REPEALS = "REPEALS"
    REPEALED_BY = "REPEALED_BY"
    CONSOLIDATES = "CONSOLIDATES"
    CONSOLIDATED_BY = "CONSOLIDATED_BY"
    IMPLEMENTS = "IMPLEMENTS"
    IMPLEMENTED_BY = "IMPLEMENTED_BY"
    TRANSPOSITION_OF = "TRANSPOSITION_OF"
    TRANSPOSED_BY = "TRANSPOSED_BY"
    LEGAL_BASIS = "LEGAL_BASIS"
    BASED_ON = "BASED_ON"
    CORRECTS = "CORRECTS"
    CORRECTED_BY = "CORRECTED_BY"
    RELATED_TO = "RELATED_TO"
