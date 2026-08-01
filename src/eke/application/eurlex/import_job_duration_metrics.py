"""Duration statistics for completed import-job executions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from eke.domain.imports import ImportJob


@dataclass(frozen=True, slots=True)
class ImportJobDurationStatistics:
    """Represent aggregate execution-duration statistics."""

    sample_count: int
    minimum_seconds: float | None
    maximum_seconds: float | None
    average_seconds: float | None

    def __post_init__(self) -> None:
        if not isinstance(self.sample_count, int):
            raise TypeError("sample_count must be an integer")
        if self.sample_count < 0:
            raise ValueError(
                "sample_count must not be negative"
            )

        values = (
            self.minimum_seconds,
            self.maximum_seconds,
            self.average_seconds,
        )
        for name, value in zip(
            (
                "minimum_seconds",
                "maximum_seconds",
                "average_seconds",
            ),
            values,
            strict=True,
        ):
            if value is not None and not isinstance(value, float):
                raise TypeError(
                    f"{name} must be a float or None"
                )
            if value is not None and value < 0:
                raise ValueError(
                    f"{name} must not be negative"
                )

        if self.sample_count == 0:
            if any(value is not None for value in values):
                raise ValueError(
                    "empty statistics must not contain values"
                )
        else:
            if any(value is None for value in values):
                raise ValueError(
                    "non-empty statistics require all values"
                )
            if (
                self.minimum_seconds is not None
                and self.maximum_seconds is not None
                and self.minimum_seconds
                > self.maximum_seconds
            ):
                raise ValueError(
                    "minimum_seconds must not exceed "
                    "maximum_seconds"
                )

    @classmethod
    def from_jobs(
        cls,
        jobs: tuple[ImportJob, ...],
    ) -> ImportJobDurationStatistics:
        """Derive duration statistics from terminal jobs."""
        if not isinstance(jobs, tuple):
            raise TypeError("jobs must be a tuple")
        if any(
            not isinstance(job, ImportJob)
            for job in jobs
        ):
            raise TypeError(
                "jobs must contain only ImportJob values"
            )

        durations = tuple(
            _duration_seconds(job)
            for job in jobs
            if (
                job.started_at is not None
                and job.completed_at is not None
            )
        )

        if not durations:
            return cls(
                sample_count=0,
                minimum_seconds=None,
                maximum_seconds=None,
                average_seconds=None,
            )

        return cls(
            sample_count=len(durations),
            minimum_seconds=float(min(durations)),
            maximum_seconds=float(max(durations)),
            average_seconds=float(
                sum(durations) / len(durations)
            ),
        )


def _duration_seconds(job: ImportJob) -> float:
    if job.started_at is None or job.completed_at is None:
        raise ValueError(
            "job must define started_at and completed_at"
        )

    duration: timedelta = (
        job.completed_at - job.started_at
    )
    seconds = duration.total_seconds()
    if seconds < 0:
        raise ValueError(
            "completed_at must not be before started_at"
        )
    return seconds
