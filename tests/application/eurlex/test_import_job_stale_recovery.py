"""Tests for explicit stale import-job recovery."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from eke.application.eurlex import (
    EurLexImportJobService,
    ImportJobSearchCriteria,
    ImportJobSearchPage,
    ImportJobStateError,
)
from eke.domain.imports import ImportJob, ImportJobStatus

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class Repository:
    def __init__(self) -> None:
        self.jobs: dict[UUID, ImportJob] = {}

    def save(self, job: ImportJob) -> None:
        self.jobs[job.job_uuid] = job

    def get(self, job_uuid: UUID) -> ImportJob | None:
        return self.jobs.get(job_uuid)

    def exists(self, job_uuid: UUID) -> bool:
        return job_uuid in self.jobs

    def search(
        self,
        criteria: ImportJobSearchCriteria,
    ) -> ImportJobSearchPage:
        jobs = tuple(self.jobs.values())
        return ImportJobSearchPage(
            items=jobs[
                criteria.offset:
                criteria.offset + criteria.limit
            ],
            total=len(jobs),
            limit=criteria.limit,
            offset=criteria.offset,
        )


class Executor:
    def import_resources(self, identifiers):
        raise AssertionError("executor must not be called")


def make_service() -> tuple[
    EurLexImportJobService,
    Repository,
]:
    repository = Repository()
    return (
        EurLexImportJobService(
            repository,
            Executor(),
            clock=lambda: NOW,
        ),
        repository,
    )


def test_recover_stale_running_job() -> None:
    service, repository = make_service()
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW - timedelta(hours=2),
    )
    running = replace(
        job,
        status=ImportJobStatus.RUNNING,
        started_at=NOW - timedelta(hours=2),
    )
    repository.save(running)

    recovered = service.recover_stale_job(
        running.job_uuid,
        threshold_seconds=3600,
    )

    assert recovered.status is ImportJobStatus.FAILED
    assert recovered.completed_at == NOW
    assert recovered.failed == recovered.total
    assert recovered.error_detail == (
        "import job exceeded stale threshold"
    )
    assert repository.get(running.job_uuid) == recovered


def test_recovery_rejects_recent_running_job() -> None:
    service, repository = make_service()
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW - timedelta(minutes=5),
    )
    running = replace(
        job,
        status=ImportJobStatus.RUNNING,
        started_at=NOW - timedelta(minutes=5),
    )
    repository.save(running)

    with pytest.raises(
        ImportJobStateError,
        match="has not exceeded",
    ):
        service.recover_stale_job(
            running.job_uuid,
            threshold_seconds=3600,
        )


def test_recovery_rejects_non_running_job() -> None:
    service, repository = make_service()
    pending = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
    )
    repository.save(pending)

    with pytest.raises(
        ImportJobStateError,
        match="only running",
    ):
        service.recover_stale_job(
            pending.job_uuid,
            threshold_seconds=3600,
        )
