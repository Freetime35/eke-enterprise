"""Tests for import-job duration statistics."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

from eke.application.eurlex import (
    ImportJobDurationStatistics,
)
from eke.domain.imports import ImportJob, ImportJobStatus

START = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


def make_completed_job(seconds: int) -> ImportJob:
    job = ImportJob.create(
        ("32023R1114",),
        created_at=START,
    )
    return replace(
        job,
        status=ImportJobStatus.COMPLETED,
        started_at=START,
        completed_at=START + timedelta(seconds=seconds),
    )


def test_duration_statistics_are_derived() -> None:
    statistics = ImportJobDurationStatistics.from_jobs(
        (
            make_completed_job(10),
            make_completed_job(20),
            make_completed_job(30),
        )
    )

    assert statistics.sample_count == 3
    assert statistics.minimum_seconds == 10.0
    assert statistics.maximum_seconds == 30.0
    assert statistics.average_seconds == 20.0


def test_jobs_without_complete_timestamps_are_ignored() -> None:
    pending = ImportJob.create(
        ("32023R1114",),
        created_at=START,
    )

    statistics = ImportJobDurationStatistics.from_jobs(
        (pending,)
    )

    assert statistics.sample_count == 0
    assert statistics.minimum_seconds is None
    assert statistics.maximum_seconds is None
    assert statistics.average_seconds is None
