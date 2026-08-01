"""Tests for persistent import jobs."""

from datetime import UTC, datetime

import pytest

from eke.domain.imports import ImportJob, ImportJobStatus

NOW = datetime(2026, 8, 1, 22, 0, tzinfo=UTC)


def test_create_pending_import_job() -> None:
    job = ImportJob.create(
        ("32023R1114", "32013R0575"),
        created_at=NOW,
    )

    assert job.status is ImportJobStatus.PENDING
    assert job.total == 2
    assert job.created_at == NOW


def test_job_rejects_naive_created_at() -> None:
    with pytest.raises(
        ValueError,
        match="created_at must be timezone-aware",
    ):
        ImportJob.create(
            ("32023R1114",),
            created_at=datetime(2026, 8, 1, 22, 0),
        )
