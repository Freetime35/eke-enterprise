"""Application service for persistent EUR-Lex import jobs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from json import dumps
from typing import Protocol
from uuid import UUID

from eke.application.eurlex.bulk_import import (
    EurLexBulkImportResult,
)
from eke.application.eurlex.import_job_duration_metrics import (
    ImportJobDurationStatistics,
)
from eke.application.eurlex.import_job_failed_items import (
    FailedImportJobResultError,
    extract_failed_celex,
)
from eke.application.eurlex.import_job_lineage import (
    ImportJobLineage,
)
from eke.application.eurlex.import_job_metrics import (
    ImportJobOperationalMetrics,
)
from eke.application.eurlex.import_job_repository import (
    ImportJobRepository,
)
from eke.application.eurlex.import_job_search import (
    ImportJobSearchCriteria,
    ImportJobSearchPage,
)
from eke.application.eurlex.import_job_staleness import (
    StaleImportJobReport,
)
from eke.application.eurlex.import_job_summary import (
    ImportJobStatusSummary,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.imports import ImportJob, ImportJobStatus


class BulkImportExecutor(Protocol):
    """Execute one deterministic bulk import request."""

    def import_resources(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> EurLexBulkImportResult:
        """Import CELEX identifiers and return all outcomes."""


class ImportJobNotFoundError(Exception):
    """Raised when an import job does not exist."""


class ImportJobStateError(Exception):
    """Raised when an import job cannot transition."""


class ImportJobLineageError(Exception):
    """Raised when persisted retry lineage is invalid."""


class EurLexImportJobService:
    """Create, inspect, execute, cancel, and retry jobs."""

    def __init__(
        self,
        repository: ImportJobRepository,
        bulk_import_executor: BulkImportExecutor,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(repository, ImportJobRepository):
            raise TypeError(
                "repository must implement ImportJobRepository"
            )
        if not hasattr(
            bulk_import_executor,
            "import_resources",
        ):
            raise TypeError(
                "bulk_import_executor must implement "
                "import_resources"
            )
        if clock is not None and not callable(clock):
            raise TypeError("clock must be callable or None")

        self._repository = repository
        self._bulk_import_executor = bulk_import_executor
        self._clock = clock or (
            lambda: datetime.now(UTC)
        )

    def create_job(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> ImportJob:
        """Create and persist a pending import job."""
        if not isinstance(identifiers, tuple):
            raise TypeError("identifiers must be a tuple")
        if not identifiers:
            raise ValueError("identifiers must not be empty")
        if any(
            not isinstance(identifier, CelexIdentifier)
            for identifier in identifiers
        ):
            raise TypeError(
                "identifiers must contain CelexIdentifier values"
            )

        celex = tuple(
            dict.fromkeys(
                identifier.value
                for identifier in identifiers
            )
        )
        job = ImportJob.create(
            celex,
            created_at=self._now(),
        )
        self._repository.save(job)

        return job

    def get_job(
        self,
        job_uuid: UUID,
    ) -> ImportJob:
        """Return one persistent import job."""
        if not isinstance(job_uuid, UUID):
            raise TypeError("job_uuid must be a UUID")

        job = self._repository.get(job_uuid)

        if job is None:
            raise ImportJobNotFoundError(
                f"import job not found: {job_uuid}"
            )

        return job

    def get_job_lineage(
        self,
        job_uuid: UUID,
    ) -> ImportJobLineage:
        """Return retry ancestors ordered from root to current."""
        current = self.get_job(job_uuid)
        reversed_items = [current]
        visited = {current.job_uuid}

        while current.retried_from_job_uuid is not None:
            parent_uuid = current.retried_from_job_uuid

            if parent_uuid in visited:
                raise ImportJobLineageError(
                    "import job retry lineage contains a cycle"
                )

            parent = self._repository.get(parent_uuid)

            if parent is None:
                raise ImportJobLineageError(
                    "import job retry lineage references "
                    f"missing job: {parent_uuid}"
                )

            visited.add(parent_uuid)
            reversed_items.append(parent)
            current = parent

        return ImportJobLineage(
            items=tuple(reversed(reversed_items))
        )

    def summarize_jobs(
        self,
    ) -> ImportJobStatusSummary:
        """Return aggregate counts for every job status."""
        counts = {
            status: self._repository.search(
                ImportJobSearchCriteria(
                    status=status,
                    limit=1,
                    offset=0,
                )
            ).total
            for status in ImportJobStatus
        }

        return ImportJobStatusSummary(
            total=sum(counts.values()),
            counts=counts,
        )

    def get_operational_metrics(
        self,
    ) -> ImportJobOperationalMetrics:
        """Return operational indicators derived from job status."""
        return ImportJobOperationalMetrics.from_summary(
            self.summarize_jobs()
        )

    def get_duration_statistics(
        self,
    ) -> ImportJobDurationStatistics:
        """Return execution-duration statistics for terminal jobs."""
        jobs: list[ImportJob] = []

        for status in (
            ImportJobStatus.COMPLETED,
            ImportJobStatus.PARTIALLY_FAILED,
            ImportJobStatus.FAILED,
        ):
            offset = 0

            while True:
                page = self._repository.search(
                    ImportJobSearchCriteria(
                        status=status,
                        limit=100,
                        offset=offset,
                    )
                )
                jobs.extend(page.items)
                offset += len(page.items)

                if offset >= page.total:
                    break

        return ImportJobDurationStatistics.from_jobs(
            tuple(jobs)
        )

    def get_stale_jobs(
        self,
        *,
        threshold_seconds: int,
    ) -> StaleImportJobReport:
        """Return running jobs older than the threshold."""
        jobs: list[ImportJob] = []
        offset = 0

        while True:
            page = self._repository.search(
                ImportJobSearchCriteria(
                    status=ImportJobStatus.RUNNING,
                    limit=100,
                    offset=offset,
                )
            )
            jobs.extend(page.items)
            offset += len(page.items)

            if offset >= page.total:
                break

        return StaleImportJobReport.from_jobs(
            tuple(jobs),
            threshold_seconds=threshold_seconds,
            observed_at=self._now(),
        )

    def recover_stale_job(
        self,
        job_uuid: UUID,
        *,
        threshold_seconds: int,
    ) -> ImportJob:
        """Mark one stale running job as failed."""
        if not isinstance(threshold_seconds, int):
            raise TypeError(
                "threshold_seconds must be an integer"
            )
        if threshold_seconds < 1:
            raise ValueError(
                "threshold_seconds must be greater than zero"
            )

        job = self.get_job(job_uuid)

        if job.status is not ImportJobStatus.RUNNING:
            raise ImportJobStateError(
                "only running import jobs can be recovered"
            )

        if job.started_at is None:
            raise ImportJobStateError(
                "running import job must define started_at"
            )

        now = self._now()
        age_seconds = (
            now - job.started_at
        ).total_seconds()

        if age_seconds < 0:
            raise ImportJobStateError(
                "import job started_at is in the future"
            )

        if age_seconds < threshold_seconds:
            raise ImportJobStateError(
                "import job has not exceeded stale threshold"
            )

        recovered = replace(
            job,
            status=ImportJobStatus.FAILED,
            completed_at=now,
            failed=job.total,
            error_detail=(
                "import job exceeded stale threshold"
            ),
        )
        self._repository.save(recovered)

        return recovered


    def retry_failed_items(
        self,
        job_uuid: UUID,
    ) -> ImportJob:
        """Create a pending job containing only failed CELEX items."""
        original = self.get_job(job_uuid)

        if original.status not in {
            ImportJobStatus.FAILED,
            ImportJobStatus.PARTIALLY_FAILED,
        }:
            raise ImportJobStateError(
                "only failed or partially failed import jobs "
                "can retry failed items"
            )

        try:
            failed_celex = extract_failed_celex(
                original.result_json
            )
        except FailedImportJobResultError as exc:
            raise ImportJobStateError(str(exc)) from exc

        identifiers: list[CelexIdentifier] = []

        for value in failed_celex:
            try:
                identifiers.append(
                    CelexIdentifier.parse(value)
                )
            except (TypeError, ValueError) as exc:
                raise ImportJobStateError(
                    "failed item contains an invalid "
                    f"CELEX identifier: {value}"
                ) from exc

        retried = ImportJob.create(
            tuple(
                identifier.value
                for identifier in identifiers
            ),
            created_at=self._now(),
            retried_from_job_uuid=original.job_uuid,
        )
        self._repository.save(retried)

        return retried
    def search_jobs(
        self,
        criteria: ImportJobSearchCriteria,
    ) -> ImportJobSearchPage:
        """Return one stable filtered page of import jobs."""
        if not isinstance(
            criteria,
            ImportJobSearchCriteria,
        ):
            raise TypeError(
                "criteria must be an ImportJobSearchCriteria"
            )

        return self._repository.search(criteria)

    def retry_job(
        self,
        job_uuid: UUID,
    ) -> ImportJob:
        """Create a new pending job from a retryable terminal job."""
        original = self.get_job(job_uuid)

        if original.status not in {
            ImportJobStatus.FAILED,
            ImportJobStatus.PARTIALLY_FAILED,
            ImportJobStatus.CANCELLED,
        }:
            raise ImportJobStateError(
                "only failed, partially failed, or cancelled "
                "import jobs can be retried"
            )

        retried = ImportJob.create(
            original.celex,
            created_at=self._now(),
            retried_from_job_uuid=original.job_uuid,
        )
        self._repository.save(retried)

        return retried

    def cancel_job(
        self,
        job_uuid: UUID,
    ) -> ImportJob:
        """Cancel a pending job before execution starts."""
        job = self.get_job(job_uuid)

        if job.status is not ImportJobStatus.PENDING:
            raise ImportJobStateError(
                "only pending import jobs can be cancelled"
            )

        cancelled = replace(
            job,
            status=ImportJobStatus.CANCELLED,
            cancelled_at=self._now(),
        )
        self._repository.save(cancelled)

        return cancelled

    def run_job(
        self,
        job_uuid: UUID,
    ) -> ImportJob:
        """Execute a pending job and persist each transition."""
        job = self.get_job(job_uuid)

        if job.status is not ImportJobStatus.PENDING:
            raise ImportJobStateError(
                "only pending import jobs can be run"
            )

        running = replace(
            job,
            status=ImportJobStatus.RUNNING,
            started_at=self._now(),
        )
        self._repository.save(running)

        try:
            result = (
                self._bulk_import_executor.import_resources(
                    tuple(
                        CelexIdentifier.parse(value)
                        for value in running.celex
                    )
                )
            )
        except Exception as exc:
            failed = replace(
                running,
                status=ImportJobStatus.FAILED,
                completed_at=self._now(),
                failed=running.total,
                error_detail=str(exc),
            )
            self._repository.save(failed)

            return failed

        completed = replace(
            running,
            status=(
                ImportJobStatus.PARTIALLY_FAILED
                if result.failed
                else ImportJobStatus.COMPLETED
            ),
            completed_at=self._now(),
            total=result.total,
            created=result.created,
            existing=result.existing,
            failed=result.failed,
            result_json=_encode_result(result),
        )
        self._repository.save(completed)

        return completed

    def _now(self) -> datetime:
        value = self._clock()

        if not isinstance(value, datetime):
            raise TypeError(
                "clock must return a datetime"
            )

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "clock must return a timezone-aware datetime"
            )

        return value


def _encode_result(
    result: EurLexBulkImportResult,
) -> str:
    return dumps(
        [
            {
                "celex": item.celex,
                "status": item.status.value,
                "resource_uuid": item.resource_uuid,
                "error_code": item.error_code,
                "detail": item.detail,
            }
            for item in result.items
        ],
        separators=(",", ":"),
        sort_keys=True,
    )