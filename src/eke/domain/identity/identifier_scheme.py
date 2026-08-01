"""Business identifier scheme enumeration.

This module defines the controlled vocabulary used to identify
external business identifier schemes supported by EKE Enterprise.
"""

from __future__ import annotations

from enum import StrEnum


class IdentifierScheme(StrEnum):
    """Represent a supported external business identifier scheme.

    Each value identifies the authority or convention under which an
    external identifier is assigned to a resource.
    """

    CELEX = "CELEX"
    ELI = "ELI"
    CELLAR = "CELLAR"
    ECLI = "ECLI"
    EURLEX = "EURLEX"
