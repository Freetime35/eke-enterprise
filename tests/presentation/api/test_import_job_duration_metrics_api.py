"""API tests for import-job duration statistics."""

from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobDurationStatistics,
)
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)


class FakeService:
    def get_duration_statistics(
        self,
    ) -> ImportJobDurationStatistics:
        return ImportJobDurationStatistics(
            sample_count=3,
            minimum_seconds=10.0,
            maximum_seconds=30.0,
            average_seconds=20.0,
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
                f"{tmp_path / 'job-durations.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_import_job_duration_statistics(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path, FakeService()) as client:
        response = client.get(
            "/imports/eurlex/jobs/durations"
        )

    assert response.status_code == 200
    assert response.json() == {
        "sample_count": 3,
        "minimum_seconds": 10.0,
        "maximum_seconds": 30.0,
        "average_seconds": 20.0,
    }
