"""Tests for the persistent EUR-Lex import job service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from json import loads
from uuid import UUID, uuid4

import pytest

from eke.application.eurlex import (
    EurLexBulkImportItem,
    EurLexBulkImportResult,
    EurLexBulkImportStatus,
    EurLexImportJobService,
    ImportJobNotFoundError,
    ImportJobSearchCriteria,
    ImportJobSearchPage,
    ImportJobStateError,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.imports import ImportJob, ImportJobStatus

START = datetime(2026, 8, 2, 8, 0, tzinfo=UTC)


class Repository:
    def __init__(self) -> None:
        self.jobs: dict[UUID, ImportJob] = {}
        self.saved_statuses: list[ImportJobStatus] = []

    def save(self, job: ImportJob) -> None:
        self.jobs[job.job_uuid] = job
        self.saved_statuses.append(job.status)

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


class SuccessfulExecutor:
    def import_resources(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> EurLexBulkImportResult:
        return EurLexBulkImportResult(
            (
                EurLexBulkImportItem(
                    celex=identifiers[0].value,
                    status=EurLexBulkImportStatus.CREATED,
                    resource_uuid=(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                ),
                EurLexBulkImportItem(
                    celex=identifiers[1].value,
                    status=EurLexBulkImportStatus.EXISTING,
                    resource_uuid=(
                        "00000000-0000-0000-0000-000000000002"
                    ),
                ),
            )
        )


class PartialExecutor:
    def import_resources(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> EurLexBulkImportResult:
        return EurLexBulkImportResult(
            (
                EurLexBulkImportItem(
                    celex=identifiers[0].value,
                    status=EurLexBulkImportStatus.CREATED,
                    resource_uuid=(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                ),
                EurLexBulkImportItem(
                    celex=identifiers[1].value,
                    status=EurLexBulkImportStatus.FAILED,
                    error_code="eurlex_client_error",
                    detail="upstream unavailable",
                ),
            )
        )


class FailingExecutor:
    def import_resources(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> EurLexBulkImportResult:
        del identifiers
        raise RuntimeError("unexpected executor failure")


def clock() -> datetime:
    current = getattr(clock, "current", START)
    clock.current = current + timedelta(seconds=1)
    return current


def make_identifiers() -> tuple[CelexIdentifier, ...]:
    return (
        CelexIdentifier.parse("32023R1114"),
        CelexIdentifier.parse("32013R0575"),
    )


def test_create_job_deduplicates_and_persists() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        SuccessfulExecutor(),
        clock=lambda: START,
    )

    job = service.create_job(
        (
            CelexIdentifier.parse("32023R1114"),
            CelexIdentifier.parse("32023R1114"),
            CelexIdentifier.parse("32013R0575"),
        )
    )

    assert job.status is ImportJobStatus.PENDING
    assert job.celex == (
        "32023R1114",
        "32013R0575",
    )
    assert repository.get(job.job_uuid) == job


def test_get_missing_job_raises() -> None:
    service = EurLexImportJobService(
        Repository(),
        SuccessfulExecutor(),
        clock=lambda: START,
    )

    with pytest.raises(
        ImportJobNotFoundError,
        match="import job not found",
    ):
        service.get_job(uuid4())


def test_run_job_persists_running_and_completed() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        SuccessfulExecutor(),
        clock=clock,
    )
    job = service.create_job(make_identifiers())

    completed = service.run_job(job.job_uuid)

    assert completed.status is ImportJobStatus.COMPLETED
    assert completed.created == 1
    assert completed.existing == 1
    assert completed.failed == 0
    assert completed.started_at is not None
    assert completed.completed_at is not None
    assert completed.result_json is not None
    assert loads(completed.result_json)[0]["status"] == (
        "CREATED"
    )
    assert repository.saved_statuses[-2:] == [
        ImportJobStatus.RUNNING,
        ImportJobStatus.COMPLETED,
    ]


def test_run_job_records_partial_failure() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        PartialExecutor(),
        clock=clock,
    )
    job = service.create_job(make_identifiers())

    completed = service.run_job(job.job_uuid)

    assert (
        completed.status
        is ImportJobStatus.PARTIALLY_FAILED
    )
    assert completed.created == 1
    assert completed.failed == 1


def test_run_job_records_unexpected_failure() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        FailingExecutor(),
        clock=clock,
    )
    job = service.create_job(make_identifiers())

    failed = service.run_job(job.job_uuid)

    assert failed.status is ImportJobStatus.FAILED
    assert failed.failed == 2
    assert failed.error_detail == (
        "unexpected executor failure"
    )


def test_run_job_rejects_non_pending_state() -> None:
    repository = Repository()
    service = EurLexImportJobService(
        repository,
        SuccessfulExecutor(),
        clock=clock,
    )
    job = service.create_job(make_identifiers())
    service.run_job(job.job_uuid)

    with pytest.raises(
        ImportJobStateError,
        match="only pending",
    ):
        service.run_job(job.job_uuid)
