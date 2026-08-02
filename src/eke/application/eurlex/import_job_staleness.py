"""Stale import-job detection values."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from eke.domain.imports import ImportJob, ImportJobStatus


@dataclass(frozen=True, slots=True)
class StaleImportJob:
    """Represent one running job that exceeded a threshold."""

    job: ImportJob
    age_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.job, ImportJob):
            raise TypeError("job must be an ImportJob")
        if self.job.status is not ImportJobStatus.RUNNING:
            raise ValueError("job must be RUNNING")
        if self.job.started_at is None:
            raise ValueError("job must define started_at")
        if not isinstance(self.age_seconds, float):
            raise TypeError("age_seconds must be a float")
        if self.age_seconds < 0:
            raise ValueError("age_seconds must not be negative")


@dataclass(frozen=True, slots=True)
class StaleImportJobReport:
    """Represent stale running jobs for one threshold."""

    threshold_seconds: int
    observed_at: datetime
    items: tuple[StaleImportJob, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.threshold_seconds, int):
            raise TypeError(
                "threshold_seconds must be an integer"
            )
        if self.threshold_seconds < 1:
            raise ValueError(
                "threshold_seconds must be greater than zero"
            )
        if not isinstance(self.observed_at, datetime):
            raise TypeError(
                "observed_at must be a datetime"
            )
        if (
            self.observed_at.tzinfo is None
            or self.observed_at.utcoffset() is None
        ):
            raise ValueError(
                "observed_at must be timezone-aware"
            )
        if any(
            not isinstance(item, StaleImportJob)
            for item in self.items
        ):
            raise TypeError(
                "items must contain StaleImportJob values"
            )

    @classmethod
    def from_jobs(
        cls,
        jobs: tuple[ImportJob, ...],
        *,
        threshold_seconds: int,
        observed_at: datetime,
    ) -> StaleImportJobReport:
        """Detect running jobs older than the threshold."""
        if not isinstance(jobs, tuple):
            raise TypeError("jobs must be a tuple")
        if not isinstance(threshold_seconds, int):
            raise TypeError(
                "threshold_seconds must be an integer"
            )
        if threshold_seconds < 1:
            raise ValueError(
                "threshold_seconds must be greater than zero"
            )
        if not isinstance(observed_at, datetime):
            raise TypeError(
                "observed_at must be a datetime"
            )
        if (
            observed_at.tzinfo is None
            or observed_at.utcoffset() is None
        ):
            raise ValueError(
                "observed_at must be timezone-aware"
            )

        threshold = timedelta(
            seconds=threshold_seconds
        )
        stale: list[StaleImportJob] = []

        for job in jobs:
            if not isinstance(job, ImportJob):
                raise TypeError(
                    "jobs must contain only ImportJob values"
                )
            if (
                job.status is not ImportJobStatus.RUNNING
                or job.started_at is None
            ):
                continue

            age = observed_at - job.started_at
            if age < timedelta(0):
                raise ValueError(
                    "started_at must not be after observed_at"
                )
            if age >= threshold:
                stale.append(
                    StaleImportJob(
                        job=job,
                        age_seconds=float(
                            age.total_seconds()
                        ),
                    )
                )

        stale.sort(
            key=lambda item: (
                item.age_seconds,
                str(item.job.job_uuid),
            ),
            reverse=True,
        )

        return cls(
            threshold_seconds=threshold_seconds,
            observed_at=observed_at,
            items=tuple(stale),
        )
