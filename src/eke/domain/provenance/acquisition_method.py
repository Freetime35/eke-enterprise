"""Acquisition method enumeration.

This module defines the canonical vocabulary used to describe how data
entered EKE Enterprise.
"""

from __future__ import annotations

from enum import StrEnum


class AcquisitionMethod(StrEnum):
    """Represent the method used to acquire source data."""

    API = "API"
    BULK_DOWNLOAD = "BULK_DOWNLOAD"
    FILE_IMPORT = "FILE_IMPORT"
    WEB_FETCH = "WEB_FETCH"
    MANUAL_ENTRY = "MANUAL_ENTRY"
    DERIVED = "DERIVED"
    OTHER = "OTHER"
