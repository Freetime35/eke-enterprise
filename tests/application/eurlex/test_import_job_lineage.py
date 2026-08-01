"""Tests for import-job retry lineage."""

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from eke.application.eurlex import (
    EurLexImportJobService,
    ImportJobLineageError,
    ImportJobSearchCriteria,
    ImportJobSearchPage,
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
    return (
        EurLexImportJobService(
            repository,
            Executor(),
            clock=lambda: NOW,
        ),
        repository,
    )


def test_lineage_returns_root_to_current() -> None:
    service, repository = make_service()
    root = service.create_job(
        (CelexIdentifier.parse("32023R1114"),)
    )
    repository.save(
        replace(root, status=ImportJobStatus.FAILED)
    )
    retry_one = service.retry_job(root.job_uuid)
    repository.save(
        replace(
            retry_one,
            status=ImportJobStatus.FAILED,
        )
    )
    retry_two = service.retry_job(retry_one.job_uuid)

    lineage = service.get_job_lineage(
        retry_two.job_uuid
    )

    assert lineage.items == (
        repository.get(root.job_uuid),
        repository.get(retry_one.job_uuid),
        retry_two,
    )
    assert lineage.root.job_uuid == root.job_uuid
    assert lineage.current.job_uuid == retry_two.job_uuid
    assert lineage.depth == 2


def test_lineage_rejects_missing_parent() -> None:
    service, repository = make_service()
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
        retried_from_job_uuid=uuid4(),
    )
    repository.save(job)

    with pytest.raises(
        ImportJobLineageError,
        match="references missing job",
    ):
        service.get_job_lineage(job.job_uuid)
