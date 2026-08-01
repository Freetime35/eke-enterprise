"""API tests for import-job operational metrics."""

from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobOperationalMetrics,
)
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)


class FakeService:
    def get_operational_metrics(
        self,
    ) -> ImportJobOperationalMetrics:
        return ImportJobOperationalMetrics(
            total=10,
            active=2,
            terminal=8,
            successful=5,
            unsuccessful=2,
            cancelled=1,
            completion_rate=0.625,
            failure_rate=0.25,
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
                f"{tmp_path / 'job-metrics.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_import_job_metrics(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path, FakeService()) as client:
        response = client.get(
            "/imports/eurlex/jobs/metrics"
        )

    assert response.status_code == 200
    assert response.json() == {
        "total": 10,
        "active": 2,
        "terminal": 8,
        "successful": 5,
        "unsuccessful": 2,
        "cancelled": 1,
        "completion_rate": 0.625,
        "failure_rate": 0.25,
    }
