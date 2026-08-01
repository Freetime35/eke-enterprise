"""API tests for import-job status summary."""

from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import ImportJobStatusSummary
from eke.domain.imports import ImportJobStatus
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)


class FakeService:
    def summarize_jobs(self) -> ImportJobStatusSummary:
        counts = {
            status: 0
            for status in ImportJobStatus
        }
        counts[ImportJobStatus.PENDING] = 3
        counts[ImportJobStatus.FAILED] = 2
        return ImportJobStatusSummary(
            total=5,
            counts=counts,
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
                f"{tmp_path / 'job-summary.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_import_job_summary(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path, FakeService()) as client:
        response = client.get(
            "/imports/eurlex/jobs/summary"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["counts"]["PENDING"] == 3
    assert body["counts"]["FAILED"] == 2
    assert body["counts"]["COMPLETED"] == 0
