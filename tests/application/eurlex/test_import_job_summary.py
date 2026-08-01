"""Tests for import-job status summaries."""

from datetime import UTC, datetime
from uuid import UUID

from eke.application.eurlex import (
    EurLexImportJobService,
    ImportJobSearchCriteria,
    ImportJobSearchPage,
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
        items = tuple(
            job
            for job in self.jobs.values()
            if (
                criteria.status is None
                or job.status is criteria.status
            )
        )
        return ImportJobSearchPage(
            items=items[
                criteria.offset:
                criteria.offset + criteria.limit
            ],
            total=len(items),
            limit=criteria.limit,
            offset=criteria.offset,
        )


class Executor:
    def import_resources(self, identifiers):
        raise AssertionError("executor must not be called")


def test_summary_counts_every_status() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        Executor(),
        clock=lambda: NOW,
    )

    for status in ImportJobStatus:
        job = ImportJob.create(
            (f"32023R{len(repository.jobs) + 1:04d}",),
            created_at=NOW,
        )
        if status is ImportJobStatus.CANCELLED:
            from dataclasses import replace
            job = replace(
                job,
                status=status,
                cancelled_at=NOW,
            )
        elif status is not ImportJobStatus.PENDING:
            from dataclasses import replace
            job = replace(job, status=status)
        repository.save(job)

    summary = service.summarize_jobs()

    assert summary.total == len(ImportJobStatus)
    for status in ImportJobStatus:
        assert summary.count(status) == 1
