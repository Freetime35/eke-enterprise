"""Application exceptions for Resource use cases."""

from __future__ import annotations


class ResourceApplicationError(Exception):
    """Base exception for Resource application use cases."""


class ResourceAlreadyExistsError(ResourceApplicationError):
    """Raised when creating a Resource that already exists."""


class ResourceNotFoundError(ResourceApplicationError):
    """Raised when a requested Resource does not exist."""
