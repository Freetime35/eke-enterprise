"""Tests for import-job cancellation."""

from datetime import UTC, datetime
from uuid import UUID

import pytest

from eke.application.eurlex import (
    EurLexImportJobService,
    ImportJobSearchCriteria,
    ImportJobSearchPage,
    ImportJobStateError,
)
from eke.domain.identity import CelexIdentifier
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


def test_cancel_pending_job() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        Executor(),
        clock=lambda: NOW,
    )
    job = service.create_job(
        (CelexIdentifier.parse("32023R1114"),)
    )

    cancelled = service.cancel_job(job.job_uuid)

    assert cancelled.status is ImportJobStatus.CANCELLED
    assert cancelled.cancelled_at == NOW
    assert repository.get(job.job_uuid) == cancelled


def test_cancel_non_pending_job_is_rejected() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        Executor(),
        clock=lambda: NOW,
    )
    job = service.create_job(
        (CelexIdentifier.parse("32023R1114"),)
    )
    service.cancel_job(job.job_uuid)

    with pytest.raises(
        ImportJobStateError,
        match="only pending",
    ):
        service.cancel_job(job.job_uuid)
