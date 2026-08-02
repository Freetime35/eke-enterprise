"""API tests for stale import-job detection."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import StaleImportJobReport
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

    def get_stale_jobs(
        self,
        *,
        threshold_seconds: int,
    ) -> StaleImportJobReport:
        return StaleImportJobReport.from_jobs(
            (self.job,),
            threshold_seconds=threshold_seconds,
            observed_at=NOW,
        )


def make_client(
    tmp_path: Path,
    service: FakeService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'job-stale.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_stale_import_jobs(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path, FakeService()) as client:
        response = client.get(
            "/imports/eurlex/jobs/stale",
            params={"threshold_seconds": 3600},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["threshold_seconds"] == 3600
    assert body["count"] == 1
    assert body["items"][0]["age_seconds"] == 7200.0
    assert body["items"][0]["job"]["status"] == "RUNNING"
