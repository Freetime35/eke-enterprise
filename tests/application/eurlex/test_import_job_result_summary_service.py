"""Service tests for import-job result summaries."""

from dataclasses import replace
from datetime import UTC, datetime
from json import dumps
from uuid import UUID

from eke.application.eurlex import (
    EurLexBulkImportStatus,
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

    def get(
        self,
        job_uuid: UUID,
    ) -> ImportJob | None:
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
        raise AssertionError(
            "executor must not be called"
        )


def test_service_summarizes_persisted_items() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        Executor(),
        clock=lambda: NOW,
    )
    job = replace(
        ImportJob.create(
            (
                "32023R1114",
                "32013R0575",
                "32024R0001",
            ),
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
                    "celex": "32013R0575",
                    "status": "EXISTING",
                },
                {
                    "celex": "32024R0001",
                    "status": "FAILED",
                },
            ]
        ),
    )
    repository.save(job)

    summary = service.get_result_summary(
        job.job_uuid
    )

    assert summary.total == 3
    assert summary.counts[
        EurLexBulkImportStatus.CREATED
    ] == 1
    assert summary.counts[
        EurLexBulkImportStatus.EXISTING
    ] == 1
    assert summary.counts[
        EurLexBulkImportStatus.FAILED
    ] == 1
