"""EUR-Lex infrastructure adapters."""

from eke.infrastructure.eurlex.full_rdf_xml_parser import (
    FullRdfXmlEurLexMetadataParser,
)
from eke.infrastructure.eurlex.httpx_client import (
    DEFAULT_CELEX_BASE_URL,
    HttpxEurLexClient,
)
from eke.infrastructure.eurlex.sqlalchemy_import_job_repository import (
    SQLAlchemyImportJobRepository,
)
from eke.infrastructure.eurlex.threaded_import_job_worker import (
    ThreadedImportJobWorker,
)

RdfXmlEurLexMetadataParser = (
    FullRdfXmlEurLexMetadataParser
)

__all__ = [
    "DEFAULT_CELEX_BASE_URL",
    "FullRdfXmlEurLexMetadataParser",
    "HttpxEurLexClient",
    "RdfXmlEurLexMetadataParser",
    "SQLAlchemyImportJobRepository",
    "ThreadedImportJobWorker",
]
