"""Tests for failed import-item inspection."""

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
        return ImportJobSearchPage(
            items=(),
            total=0,
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


def test_get_failed_items_returns_details() -> None:
    service, repository = make_service()
    job = replace(
        ImportJob.create(
            ("32023R1114", "32024R0001"),
            created_at=NOW,
        ),
        status=ImportJobStatus.PARTIALLY_FAILED,
        result_json=dumps(
            [
                {
                    "celex": "32023R1114",
                    "status": "CREATED",
                },
                {
                    "celex": "32024R0001",
                    "status": "FAILED",
                    "error_code": "INVALID_METADATA",
                    "detail": "missing resource type",
                },
            ]
        ),
    )
    repository.save(job)

    items = service.get_failed_items(job.job_uuid)

    assert len(items) == 1
    assert items[0].celex == "32024R0001"
    assert items[0].error_code == "INVALID_METADATA"
    assert items[0].detail == "missing resource type"


def test_get_failed_items_rejects_pending_job() -> None:
    service, repository = make_service()
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
    )
    repository.save(job)

    with pytest.raises(
        ImportJobStateError,
        match="only failed or partially failed",
    ):
        service.get_failed_items(job.job_uuid)
