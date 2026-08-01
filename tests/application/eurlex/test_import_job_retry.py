"""Tests for import-job retry."""

from dataclasses import replace
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
            items=jobs,
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
    service = EurLexImportJobService(
        repository,
        Executor(),
        clock=lambda: NOW,
    )
    return service, repository


@pytest.mark.parametrize(
    "status",
    [
        ImportJobStatus.FAILED,
        ImportJobStatus.PARTIALLY_FAILED,
        ImportJobStatus.CANCELLED,
    ],
)
def test_retry_creates_new_pending_job(
    status: ImportJobStatus,
) -> None:
    service, repository = make_service()
    original = service.create_job(
        (CelexIdentifier.parse("32023R1114"),)
    )
    terminal = replace(
        original,
        status=status,
        cancelled_at=(
            NOW if status is ImportJobStatus.CANCELLED else None
        ),
    )
    repository.save(terminal)

    retried = service.retry_job(original.job_uuid)

    assert retried.job_uuid != original.job_uuid
    assert retried.status is ImportJobStatus.PENDING
    assert retried.celex == original.celex
    assert (
        retried.retried_from_job_uuid
        == original.job_uuid
    )


def test_retry_rejects_completed_job() -> None:
    service, repository = make_service()
    original = service.create_job(
        (CelexIdentifier.parse("32023R1114"),)
    )
    repository.save(
        replace(
            original,
            status=ImportJobStatus.COMPLETED,
        )
    )

    with pytest.raises(
        ImportJobStateError,
        match="can be retried",
    ):
        service.retry_job(original.job_uuid)
