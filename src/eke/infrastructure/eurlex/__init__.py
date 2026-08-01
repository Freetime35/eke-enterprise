"""EUR-Lex infrastructure adapters."""

from eke.infrastructure.eurlex.httpx_client import (
    DEFAULT_CELEX_BASE_URL,
    HttpxEurLexClient,
)
from eke.infrastructure.eurlex.rdf_xml_parser import (
    RdfXmlEurLexMetadataParser,
)

__all__ = [
    "DEFAULT_CELEX_BASE_URL",
    "HttpxEurLexClient",
    "RdfXmlEurLexMetadataParser",
]
