"""EUR-Lex infrastructure adapters."""

from eke.infrastructure.eurlex.full_rdf_xml_parser import (
    FullRdfXmlEurLexMetadataParser,
)
from eke.infrastructure.eurlex.httpx_client import (
    DEFAULT_CELEX_BASE_URL,
    HttpxEurLexClient,
)

RdfXmlEurLexMetadataParser = FullRdfXmlEurLexMetadataParser

__all__ = [
    "DEFAULT_CELEX_BASE_URL",
    "FullRdfXmlEurLexMetadataParser",
    "HttpxEurLexClient",
    "RdfXmlEurLexMetadataParser",
]
