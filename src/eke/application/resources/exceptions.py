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


class ResourceVersionAlreadyExistsError(ResourceApplicationError):
    """Raised when an identical ResourceVersion already exists."""


class ResourceVersionNotFoundError(ResourceApplicationError):
    """Raised when a requested ResourceVersion does not exist."""


class ResourceVersionConflictError(ResourceApplicationError):
    """Raised when a ResourceVersion operation violates version history."""


class ResourceRelationshipAlreadyExistsError(
    ResourceApplicationError
):
    """Raised when an identical relationship already exists."""


class ResourceRelationshipNotFoundError(ResourceApplicationError):
    """Raised when a requested relationship does not exist."""


class ResourceRelationshipConflictError(ResourceApplicationError):
    """Raised when a relationship operation is inconsistent."""


class ProvenanceRecordAlreadyExistsError(
    ResourceApplicationError
):
    """Raised when an identical ProvenanceRecord already exists."""


class ProvenanceRecordNotFoundError(ResourceApplicationError):
    """Raised when a requested ProvenanceRecord does not exist."""


class ProvenanceRecordConflictError(ResourceApplicationError):
    """Raised when provenance does not belong to the Resource."""


class ResourceClassificationAlreadyExistsError(
    ResourceApplicationError
):
    """Raised when a classification key is already assigned."""


class ResourceClassificationNotFoundError(
    ResourceApplicationError
):
    """Raised when a requested classification does not exist."""
