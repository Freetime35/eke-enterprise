"""API tests for stale import-job recovery."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobNotFoundError,
    ImportJobStateError,
)
from eke.domain.imports import ImportJob, ImportJobStatus
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeService:
    def __init__(self) -> None:
        job = ImportJob.create(
            ("32023R1114",),
            created_at=NOW - timedelta(hours=2),
        )
        self.job = replace(
            job,
            status=ImportJobStatus.RUNNING,
            started_at=NOW - timedelta(hours=2),
        )

    def recover_stale_job(
        self,
        job_uuid: UUID,
        *,
        threshold_seconds: int,
    ) -> ImportJob:
        if job_uuid != self.job.job_uuid:
            raise ImportJobNotFoundError(
                "import job not found"
            )
        if threshold_seconds > 7200:
            raise ImportJobStateError(
                "import job has not exceeded stale threshold"
            )

        self.job = replace(
            self.job,
            status=ImportJobStatus.FAILED,
            completed_at=NOW,
            failed=self.job.total,
            error_detail=(
                "import job exceeded stale threshold"
            ),
        )
        return self.job


def make_client(
    tmp_path: Path,
    service: FakeService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'stale-recovery.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_recover_stale_import_job(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            f"/imports/eurlex/jobs/"
            f"{service.job.job_uuid}/recover-stale",
            params={"threshold_seconds": 3600},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FAILED"
    assert body["failed"] == 1
    assert body["error_detail"] == (
        "import job exceeded stale threshold"
    )


def test_recovery_returns_409_when_not_stale(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            f"/imports/eurlex/jobs/"
            f"{service.job.job_uuid}/recover-stale",
            params={"threshold_seconds": 10000},
        )

    assert response.status_code == 409
