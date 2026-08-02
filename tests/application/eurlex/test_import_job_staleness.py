"""Tests for stale import-job detection."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from eke.application.eurlex import StaleImportJobReport
from eke.domain.imports import ImportJob, ImportJobStatus

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


def make_running_job(age_seconds: int) -> ImportJob:
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW - timedelta(seconds=age_seconds),
    )
    return replace(
        job,
        status=ImportJobStatus.RUNNING,
        started_at=NOW - timedelta(seconds=age_seconds),
    )


def test_report_returns_only_stale_running_jobs() -> None:
    stale = make_running_job(7200)
    recent = make_running_job(300)
    pending = ImportJob.create(
        ("32013R0575",),
        created_at=NOW,
    )

    report = StaleImportJobReport.from_jobs(
        (recent, pending, stale),
        threshold_seconds=3600,
        observed_at=NOW,
    )

    assert report.threshold_seconds == 3600
    assert len(report.items) == 1
    assert report.items[0].job == stale
    assert report.items[0].age_seconds == 7200.0


def test_future_started_at_is_rejected() -> None:
    future = make_running_job(-60)

    with pytest.raises(
        ValueError,
        match="must not be after observed_at",
    ):
        StaleImportJobReport.from_jobs(
            (future,),
            threshold_seconds=60,
            observed_at=NOW,
        )
