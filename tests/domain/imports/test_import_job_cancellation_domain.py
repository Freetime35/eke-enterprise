"""Tests for cancelled import jobs."""

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from eke.domain.imports import ImportJob, ImportJobStatus

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


def test_cancelled_job_requires_timestamp() -> None:
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
    )

    with pytest.raises(
        ValueError,
        match="must define cancelled_at",
    ):
        replace(
            job,
            status=ImportJobStatus.CANCELLED,
        )


def test_cancelled_job_accepts_timestamp() -> None:
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
    )

    cancelled = replace(
        job,
        status=ImportJobStatus.CANCELLED,
        cancelled_at=NOW,
    )

    assert cancelled.status is ImportJobStatus.CANCELLED
