"""SQLAlchemy ImportJobRepository implementation."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from eke.application.eurlex import (
    ImportJobRepository,
    ImportJobSearchCriteria,
    ImportJobSearchPage,
)
from eke.domain.imports import ImportJob
from eke.infrastructure.database.models import (
    ImportJobModel,
)
from eke.infrastructure.eurlex.import_job_codec import (
    IMPORT_JOB_PAYLOAD_VERSION,
    decode_import_job,
    encode_import_job,
)


class SQLAlchemyImportJobRepository:
    """Persist and search import jobs through SQLAlchemy."""

    def __init__(
        self,
        session_source: Session | sessionmaker[Session],
    ) -> None:
        if not isinstance(
            session_source,
            (Session, sessionmaker),
        ):
            raise TypeError(
                "session_source must be a Session or sessionmaker"
            )
        self._session_source = session_source

    @contextmanager
    def _session(
        self,
        *,
        write: bool = False,
    ) -> Iterator[Session]:
        if isinstance(self._session_source, Session):
            yield self._session_source
            return

        if write:
            with self._session_source.begin() as session:
                yield session
        else:
            with self._session_source() as session:
                yield session

    def save(self, job: ImportJob) -> None:
        if not isinstance(job, ImportJob):
            raise TypeError("job must be an ImportJob")

        with self._session(write=True) as session:
            model = session.get(
                ImportJobModel,
                str(job.job_uuid),
            )
            if model is None:
                model = ImportJobModel(
                    job_uuid=str(job.job_uuid),
                    status=job.status.value,
                    payload_version=(
                        IMPORT_JOB_PAYLOAD_VERSION
                    ),
                    payload=encode_import_job(job),
                    created_at=job.created_at,
                )
                session.add(model)
            else:
                model.status = job.status.value
                model.payload_version = (
                    IMPORT_JOB_PAYLOAD_VERSION
                )
                model.payload = encode_import_job(job)
            session.flush()

    def get(
        self,
        job_uuid: UUID,
    ) -> ImportJob | None:
        self._validate_job_uuid(job_uuid)
        with self._session() as session:
            model = session.get(
                ImportJobModel,
                str(job_uuid),
            )
            return (
                decode_import_job(model.payload)
                if model is not None
                else None
            )

    def exists(self, job_uuid: UUID) -> bool:
        self._validate_job_uuid(job_uuid)
        with self._session() as session:
            return (
                session.get(
                    ImportJobModel,
                    str(job_uuid),
                )
                is not None
            )

    def search(
        self,
        criteria: ImportJobSearchCriteria,
    ) -> ImportJobSearchPage:
        if not isinstance(
            criteria,
            ImportJobSearchCriteria,
        ):
            raise TypeError(
                "criteria must be an ImportJobSearchCriteria"
            )

        filters = []
        if criteria.status is not None:
            filters.append(
                ImportJobModel.status
                == criteria.status.value
            )
        if criteria.created_from is not None:
            filters.append(
                ImportJobModel.created_at
                >= criteria.created_from
            )
        if criteria.created_to is not None:
            filters.append(
                ImportJobModel.created_at
                <= criteria.created_to
            )

        with self._session() as session:
            total = session.scalar(
                select(func.count())
                .select_from(ImportJobModel)
                .where(*filters)
            )
            models = session.scalars(
                select(ImportJobModel)
                .where(*filters)
                .order_by(
                    ImportJobModel.created_at.desc(),
                    ImportJobModel.job_uuid.desc(),
                )
                .offset(criteria.offset)
                .limit(criteria.limit)
            ).all()

        return ImportJobSearchPage(
            items=tuple(
                decode_import_job(model.payload)
                for model in models
            ),
            total=int(total or 0),
            limit=criteria.limit,
            offset=criteria.offset,
        )

    @staticmethod
    def _validate_job_uuid(job_uuid: UUID) -> None:
        if not isinstance(job_uuid, UUID):
            raise TypeError("job_uuid must be a UUID")


import_job_repository_contract: type[ImportJobRepository]
import_job_repository_contract = (
    SQLAlchemyImportJobRepository
)
