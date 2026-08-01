"""Provenance source enumeration.

This module defines the canonical vocabulary used to identify the
authoritative or operational source of acquired resource data.
"""

from __future__ import annotations

from enum import StrEnum


class ProvenanceSource(StrEnum):
    """Represent the canonical source of a provenance record."""

    EUR_LEX = "EUR_LEX"
    CELLAR = "CELLAR"
    ELI = "ELI"
    ECB = "ECB"
    EBA = "EBA"
    ESMA = "ESMA"
    EIOPA = "EIOPA"
    SRB = "SRB"
    MANUAL = "MANUAL"
    OTHER = "OTHER"
