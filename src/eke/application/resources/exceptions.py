"""Application exceptions for Resource use cases."""

class ResourceApplicationError(Exception):
    """Base exception for Resource application use cases."""

class ResourceAlreadyExistsError(ResourceApplicationError):
    """Raised when creating a Resource that already exists."""

class ResourceNotFoundError(ResourceApplicationError):
    """Raised when a requested Resource does not exist."""

class ResourceTitleAlreadyExistsError(ResourceApplicationError):
    """Raised when an identical ResourceTitle already exists."""

class ResourceTitleNotFoundError(ResourceApplicationError):
    """Raised when a requested ResourceTitle does not exist."""
