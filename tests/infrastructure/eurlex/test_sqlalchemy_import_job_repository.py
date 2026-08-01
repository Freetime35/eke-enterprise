"""Tests for SQLAlchemy import job persistence."""

from datetime import UTC, datetime
from uuid import uuid4

from eke.application.eurlex import ImportJobRepository
from eke.domain.imports import ImportJob
from eke.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    upgrade_database,
)
from eke.infrastructure.eurlex import (
    SQLAlchemyImportJobRepository,
)

NOW = datetime(2026, 8, 1, 22, 0, tzinfo=UTC)


def make_repository() -> SQLAlchemyImportJobRepository:
    engine = create_sqlite_engine(
        "sqlite+pysqlite:///:memory:"
    )
    upgrade_database(engine)
    return SQLAlchemyImportJobRepository(
        create_session_factory(engine)
    )


def test_repository_satisfies_protocol() -> None:
    repository = make_repository()

    assert isinstance(repository, ImportJobRepository)


def test_repository_round_trip_preserves_job() -> None:
    repository = make_repository()
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
    )

    repository.save(job)

    assert repository.get(job.job_uuid) == job
    assert repository.exists(job.job_uuid)


def test_repository_returns_none_for_missing_job() -> None:
    repository = make_repository()

    assert repository.get(uuid4()) is None
