"""Tests for retrying only failed import-job items."""

from dataclasses import replace
from datetime import UTC, datetime
from json import dumps
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


def test_retry_failed_items_creates_selective_job() -> None:
    service, repository = make_service()
    original = ImportJob.create(
        ("32023R1114", "32013R0575", "32024R0001"),
        created_at=NOW,
    )
    partial = replace(
        original,
        status=ImportJobStatus.PARTIALLY_FAILED,
        failed=2,
        result_json=dumps(
            [
                {"celex": "32023R1114", "status": "CREATED"},
                {"celex": "32013R0575", "status": "FAILED"},
                {"celex": "32024R0001", "status": "FAILED"},
            ]
        ),
    )
    repository.save(partial)

    retried = service.retry_failed_items(partial.job_uuid)

    assert retried.status is ImportJobStatus.PENDING
    assert retried.celex == ("32013R0575", "32024R0001")
    assert retried.retried_from_job_uuid == partial.job_uuid


def test_retry_failed_items_rejects_missing_results() -> None:
    service, repository = make_service()
    failed = replace(
        ImportJob.create(("32023R1114",), created_at=NOW),
        status=ImportJobStatus.FAILED,
    )
    repository.save(failed)

    with pytest.raises(
        ImportJobStateError,
        match="no persisted item results",
    ):
        service.retry_failed_items(failed.job_uuid)


def test_retry_failed_items_rejects_no_failures() -> None:
    service, repository = make_service()
    partial = replace(
        ImportJob.create(("32023R1114",), created_at=NOW),
        status=ImportJobStatus.PARTIALLY_FAILED,
        result_json=dumps(
            [{"celex": "32023R1114", "status": "CREATED"}]
        ),
    )
    repository.save(partial)

    with pytest.raises(
        ImportJobStateError,
        match="no failed items",
    ):
        service.retry_failed_items(partial.job_uuid)
