"""Tests for SQLAlchemy import-job search."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from eke.application.eurlex import (
    ImportJobSearchCriteria,
)
from eke.domain.imports import ImportJob, ImportJobStatus
from eke.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    upgrade_database,
)
from eke.infrastructure.eurlex import (
    SQLAlchemyImportJobRepository,
)

BASE = datetime(2026, 8, 2, 8, 0, tzinfo=UTC)


def make_repository() -> SQLAlchemyImportJobRepository:
    engine = create_sqlite_engine(
        "sqlite+pysqlite:///:memory:"
    )
    upgrade_database(engine)
    return SQLAlchemyImportJobRepository(
        create_session_factory(engine)
    )


def make_job(
    index: int,
    status: ImportJobStatus,
) -> ImportJob:
    job = ImportJob.create(
        (f"3202{index}R1114",),
        created_at=BASE + timedelta(minutes=index),
    )
    return replace(job, status=status)


def test_search_filters_status_and_paginates() -> None:
    repository = make_repository()
    jobs = (
        make_job(1, ImportJobStatus.COMPLETED),
        make_job(2, ImportJobStatus.FAILED),
        make_job(3, ImportJobStatus.FAILED),
    )
    for job in jobs:
        repository.save(job)

    page = repository.search(
        ImportJobSearchCriteria(
            status=ImportJobStatus.FAILED,
            limit=1,
            offset=0,
        )
    )

    assert page.total == 2
    assert page.limit == 1
    assert len(page.items) == 1
    assert page.items[0].job_uuid == jobs[2].job_uuid


def test_search_filters_creation_window() -> None:
    repository = make_repository()
    jobs = (
        make_job(1, ImportJobStatus.PENDING),
        make_job(2, ImportJobStatus.PENDING),
        make_job(3, ImportJobStatus.PENDING),
    )
    for job in jobs:
        repository.save(job)

    page = repository.search(
        ImportJobSearchCriteria(
            created_from=BASE + timedelta(minutes=2),
            created_to=BASE + timedelta(minutes=2),
        )
    )

    assert page.total == 1
    assert page.items == (jobs[1],)
