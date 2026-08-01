"""Application-facing EUR-Lex failures."""


class EurLexClientError(Exception):
    """Base exception for EUR-Lex retrieval failures."""


class EurLexDocumentNotFoundError(EurLexClientError):
    """Raised when no document exists for a CELEX identifier."""


class EurLexUpstreamError(EurLexClientError):
    """Raised when the upstream service cannot fulfill a request."""


class EurLexMetadataError(Exception):
    """Base exception for metadata parsing failures."""


class EurLexUnsupportedMediaTypeError(EurLexMetadataError):
    """Raised when a document is not supported by the parser."""


class EurLexMalformedMetadataError(EurLexMetadataError):
    """Raised when the metadata payload is malformed."""


class EurLexMetadataMismatchError(EurLexMetadataError):
    """Raised when payload metadata references another CELEX."""
