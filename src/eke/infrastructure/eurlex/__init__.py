"""EUR-Lex infrastructure adapters."""

from eke.infrastructure.eurlex.complex_document_content_parser import (
    EurLexComplexDocumentContentParseError,
    XmlEurLexComplexContentParser,
)
from eke.infrastructure.eurlex.document_structure_parser import (
    EurLexDocumentStructureParseError,
    XmlEurLexDocumentStructureParser,
)
from eke.infrastructure.eurlex.full_rdf_xml_parser import (
    FullRdfXmlEurLexMetadataParser,
)
from eke.infrastructure.eurlex.httpx_client import (
    DEFAULT_CELEX_BASE_URL,
    HttpxEurLexClient,
)
from eke.infrastructure.eurlex.internal_reference_parser import (
    EurLexInternalReferenceParseError,
    EurLexInternalReferenceParser,
)
from eke.infrastructure.eurlex.legal_definition_parser import (
    EurLexLegalDefinitionParseError,
    EurLexLegalDefinitionParser,
)
from eke.infrastructure.eurlex.legal_obligation_parser import (
    EurLexLegalObligationParseError,
    EurLexLegalObligationParser,
)
from eke.infrastructure.eurlex.legal_permission_parser import (
    EurLexLegalPermissionParseError,
    EurLexLegalPermissionParser,
)
from eke.infrastructure.eurlex.legal_prohibition_parser import (
    EurLexLegalProhibitionParseError,
    EurLexLegalProhibitionParser,
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
    "EurLexInternalReferenceParser",
    "EurLexInternalReferenceParseError",
    "EurLexLegalProhibitionParser",
    "EurLexLegalProhibitionParseError",
    "EurLexLegalPermissionParser",
    "EurLexLegalPermissionParseError",
    "EurLexLegalObligationParser",
    "EurLexLegalObligationParseError",
    "EurLexLegalDefinitionParser",
    "EurLexLegalDefinitionParseError",
    "XmlEurLexComplexContentParser",
    "EurLexComplexDocumentContentParseError",
    "DEFAULT_CELEX_BASE_URL",
    "EurLexDocumentStructureParseError",
    "FullRdfXmlEurLexMetadataParser",
    "HttpxEurLexClient",
    "RdfXmlEurLexMetadataParser",
    "SQLAlchemyImportJobRepository",
    "ThreadedImportJobWorker",
    "XmlEurLexDocumentStructureParser",
]