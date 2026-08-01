"""Application workflow for importing one EUR-Lex Resource."""

from __future__ import annotations

from collections.abc import Callable

from eke.application.eurlex.client import EurLexClient
from eke.application.eurlex.import_result import EurLexImportResult
from eke.application.eurlex.parser import EurLexMetadataParser
from eke.application.eurlex.resource_mapper import (
    resource_from_eurlex,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import CelexIdentifier


class EurLexResourceImportService:
    """Import one canonical Resource by CELEX identifier."""

    def __init__(
        self,
        client: EurLexClient,
        parser: EurLexMetadataParser,
        unit_of_work_factory: Callable[[], UnitOfWork],
    ) -> None:
        if not isinstance(client, EurLexClient):
            raise TypeError(
                "client must implement EurLexClient"
            )
        if not isinstance(parser, EurLexMetadataParser):
            raise TypeError(
                "parser must implement EurLexMetadataParser"
            )
        if not callable(unit_of_work_factory):
            raise TypeError(
                "unit_of_work_factory must be callable"
            )

        self._client = client
        self._parser = parser
        self._unit_of_work_factory = unit_of_work_factory

    def import_resource(
        self,
        celex_identifier: CelexIdentifier,
    ) -> EurLexImportResult:
        """Return an existing Resource or atomically import a new one."""
        if not isinstance(
            celex_identifier,
            CelexIdentifier,
        ):
            raise TypeError(
                "celex_identifier must be a CelexIdentifier"
            )

        business_identifier = (
            celex_identifier.to_business_identifier()
        )

        with self._unit_of_work_factory() as uow:
            existing = uow.resources.get_by_identifier(
                business_identifier
            )
            if existing is not None:
                return EurLexImportResult(
                    resource=existing,
                    created=False,
                )

            document = self._client.fetch_document(
                celex_identifier,
                accept="application/rdf+xml",
            )
            metadata = self._parser.parse(document)
            resource = resource_from_eurlex(
                document,
                metadata,
            )

            concurrent = uow.resources.get_by_identifier(
                business_identifier
            )
            if concurrent is not None:
                return EurLexImportResult(
                    resource=concurrent,
                    created=False,
                )

            uow.resources.save(resource)
            uow.commit()

            return EurLexImportResult(
                resource=resource,
                created=True,
            )
