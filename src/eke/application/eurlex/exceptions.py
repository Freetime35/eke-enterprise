"""Application-facing EUR-Lex client failures."""


class EurLexClientError(Exception):
    """Base exception for EUR-Lex retrieval failures."""


class EurLexDocumentNotFoundError(EurLexClientError):
    """Raised when no document exists for a CELEX identifier."""


class EurLexUpstreamError(EurLexClientError):
    """Raised when the upstream service cannot fulfill a request."""
