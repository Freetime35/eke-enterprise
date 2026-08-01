"""Resource type enumeration.

This module defines the controlled vocabulary used to classify canonical
resources by their legal or documentary nature.
"""

from __future__ import annotations

from enum import StrEnum


class ResourceType(StrEnum):
    """Represent the canonical type of a resource.

    Values are intentionally source-independent and may be mapped from
    EUR-Lex, CELLAR, ELI, or future source-specific classifications.
    """

    REGULATION = "REGULATION"
    DIRECTIVE = "DIRECTIVE"
    DECISION = "DECISION"
    RECOMMENDATION = "RECOMMENDATION"
    OPINION = "OPINION"
    TREATY = "TREATY"
    CASE_LAW = "CASE_LAW"
    NOTICE = "NOTICE"
    COMMUNICATION = "COMMUNICATION"
    GUIDELINE = "GUIDELINE"
    REPORT = "REPORT"
    PROPOSAL = "PROPOSAL"
    CORRIGENDUM = "CORRIGENDUM"
    OTHER = "OTHER"
