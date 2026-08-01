"""Application composition container."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from eke.application import UnitOfWork
from eke.application.eurlex import (
    EurLexBulkImportService,
    EurLexClient,
    EurLexImportJobService,
    EurLexMetadataParser,
    EurLexResourceImportService,
    ImportJobRepository,
    ImportJobWorker,
)
from eke.application.resources import (
    ResourceClassificationService,
    ResourceProvenanceService,
    ResourceRelationshipService,
    ResourceService,
    ResourceTitleService,
    ResourceVersionService,
)
from eke.infrastructure.eurlex import (
    HttpxEurLexClient,
    RdfXmlEurLexMetadataParser,
    SQLAlchemyImportJobRepository,
    ThreadedImportJobWorker,
)
from eke.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    """Hold application services and infrastructure adapters."""

    engine: Engine
    session_factory: sessionmaker[Session]
    unit_of_work_factory: Callable[[], UnitOfWork]
    eurlex_client: EurLexClient
    eurlex_metadata_parser: EurLexMetadataParser
    _import_job_repository: ImportJobRepository
    _import_job_service: EurLexImportJobService
    _import_job_worker: ImportJobWorker

    def resource_service(self) -> ResourceService:
        return ResourceService(self.unit_of_work_factory)

    def resource_title_service(self) -> ResourceTitleService:
        return ResourceTitleService(self.unit_of_work_factory)

    def resource_version_service(self) -> ResourceVersionService:
        return ResourceVersionService(self.unit_of_work_factory)

    def resource_relationship_service(
        self,
    ) -> ResourceRelationshipService:
        return ResourceRelationshipService(
            self.unit_of_work_factory
        )

    def resource_provenance_service(
        self,
    ) -> ResourceProvenanceService:
        return ResourceProvenanceService(
            self.unit_of_work_factory
        )

    def resource_classification_service(
        self,
    ) -> ResourceClassificationService:
        return ResourceClassificationService(
            self.unit_of_work_factory
        )

    def eurlex_import_service(
        self,
    ) -> EurLexResourceImportService:
        return EurLexResourceImportService(
            client=self.eurlex_client,
            parser=self.eurlex_metadata_parser,
            unit_of_work_factory=self.unit_of_work_factory,
        )

    def eurlex_bulk_import_service(
        self,
    ) -> EurLexBulkImportService:
        return EurLexBulkImportService(
            self.eurlex_import_service()
        )

    def import_job_repository(
        self,
    ) -> ImportJobRepository:
        return self._import_job_repository

    def import_job_service(
        self,
    ) -> EurLexImportJobService:
        return self._import_job_service

    def import_job_worker(self) -> ImportJobWorker:
        return self._import_job_worker


def build_container(
    engine: Engine,
    session_factory: sessionmaker[Session],
    *,
    eurlex_client: EurLexClient | None = None,
    eurlex_metadata_parser: EurLexMetadataParser | None = None,
    import_job_worker_max_workers: int = 2,
) -> ApplicationContainer:
    """Build the application dependency container."""
    if not isinstance(engine, Engine):
        raise TypeError("engine must be an Engine")
    if not isinstance(session_factory, sessionmaker):
        raise TypeError(
            "session_factory must be a sessionmaker"
        )

    resolved_client = eurlex_client or HttpxEurLexClient()
    resolved_parser = (
        eurlex_metadata_parser
        or RdfXmlEurLexMetadataParser()
    )

    if not isinstance(resolved_client, EurLexClient):
        raise TypeError(
            "eurlex_client must implement EurLexClient"
        )
    if not isinstance(
        resolved_parser,
        EurLexMetadataParser,
    ):
        raise TypeError(
            "eurlex_metadata_parser must implement "
            "EurLexMetadataParser"
        )

    def unit_of_work_factory() -> UnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory)

    resource_import_service = EurLexResourceImportService(
        client=resolved_client,
        parser=resolved_parser,
        unit_of_work_factory=unit_of_work_factory,
    )
    bulk_import_service = EurLexBulkImportService(
        resource_import_service
    )
    import_job_repository = SQLAlchemyImportJobRepository(
        session_factory
    )
    import_job_service = EurLexImportJobService(
        repository=import_job_repository,
        bulk_import_executor=bulk_import_service,
    )
    import_job_worker = ThreadedImportJobWorker(
        import_job_service,
        max_workers=import_job_worker_max_workers,
    )

    return ApplicationContainer(
        engine=engine,
        session_factory=session_factory,
        unit_of_work_factory=unit_of_work_factory,
        eurlex_client=resolved_client,
        eurlex_metadata_parser=resolved_parser,
        _import_job_repository=import_job_repository,
        _import_job_service=import_job_service,
        _import_job_worker=import_job_worker,
    )
