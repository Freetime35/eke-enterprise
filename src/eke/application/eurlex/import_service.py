"""Application workflow for importing a complete EUR-Lex Resource."""

from __future__ import annotations

from collections.abc import Callable

from eke.application.eurlex.client import EurLexClient
from eke.application.eurlex.full_resource_mapper import (
    map_classifications,
    map_relationships,
    map_version,
)
from eke.application.eurlex.import_result import EurLexImportResult
from eke.application.eurlex.parser import EurLexMetadataParser
from eke.application.eurlex.resource_mapper import resource_from_eurlex
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import CelexIdentifier, ResourceUUID
from eke.domain.resources import Resource


class EurLexResourceImportService:
    """Import one complete canonical Resource by CELEX identifier."""

    def __init__(
        self,
        client: EurLexClient,
        parser: EurLexMetadataParser,
        unit_of_work_factory: Callable[[], UnitOfWork],
    ) -> None:
        if not isinstance(client, EurLexClient):
            raise TypeError("client must implement EurLexClient")
        if not isinstance(parser, EurLexMetadataParser):
            raise TypeError("parser must implement EurLexMetadataParser")
        if not callable(unit_of_work_factory):
            raise TypeError("unit_of_work_factory must be callable")
        self._client = client
        self._parser = parser
        self._unit_of_work_factory = unit_of_work_factory

    def import_resource(
        self,
        celex_identifier: CelexIdentifier,
    ) -> EurLexImportResult:
        if not isinstance(celex_identifier, CelexIdentifier):
            raise TypeError(
                "celex_identifier must be a CelexIdentifier"
            )

        identifier = celex_identifier.to_business_identifier()
        with self._unit_of_work_factory() as uow:
            existing = uow.resources.get_by_identifier(identifier)
            if existing is not None:
                return EurLexImportResult(existing, False)

            document = self._client.fetch_document(
                celex_identifier,
                accept="application/rdf+xml",
            )
            metadata = self._parser.parse(document)
            base = resource_from_eurlex(document, metadata)

            targets: dict[str, ResourceUUID] = {}
            for relationship in metadata.relationships:
                target_identifier = (
                    relationship.target_celex.to_business_identifier()
                )
                target = uow.resources.get_by_identifier(
                    target_identifier
                )
                if target is None:
                    target = Resource(
                        resource_uuid=ResourceUUID.generate(),
                        identifiers=(target_identifier,),
                    )
                    uow.resources.save(target)
                targets[
                    relationship.target_celex.value
                ] = target.resource_uuid

            resource = Resource(
                resource_uuid=base.resource_uuid,
                identifiers=base.identifiers,
                resource_type=base.resource_type,
                status=base.status,
                titles=base.titles,
                versions=(map_version(base.resource_uuid, metadata),),
                relationships=map_relationships(
                    base.resource_uuid,
                    metadata,
                    targets,
                ),
                provenance_records=base.provenance_records,
                classifications=map_classifications(metadata),
            )

            concurrent = uow.resources.get_by_identifier(identifier)
            if concurrent is not None:
                return EurLexImportResult(concurrent, False)

            uow.resources.save(resource)
            uow.commit()
            return EurLexImportResult(resource, True)
