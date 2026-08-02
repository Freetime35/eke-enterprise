"""API tests for failed-item import-job retry."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import ImportJobStateError
from eke.domain.imports import ImportJob
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeService:
    def __init__(self) -> None:
        self.original_uuid = UUID(
            "00000000-0000-0000-0000-000000000001"
        )
        self.retried = ImportJob.create(
            ("32013R0575", "32024R0001"),
            created_at=NOW,
            retried_from_job_uuid=self.original_uuid,
        )

    def retry_failed_items(
        self,
        job_uuid: UUID,
    ) -> ImportJob:
        if job_uuid != self.original_uuid:
            raise ImportJobStateError(
                "import job has no failed items to retry"
            )
        return self.retried


def make_client(
    tmp_path: Path,
    service: FakeService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'failed-item-retry.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_retry_failed_items_returns_created(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            f"/imports/eurlex/jobs/"
            f"{service.original_uuid}/retry-failed"
        )

    assert response.status_code == 201
    assert response.headers["location"] == (
        f"/imports/eurlex/jobs/{service.retried.job_uuid}"
    )
    assert response.json()["celex"] == [
        "32013R0575",
        "32024R0001",
    ]


def test_retry_failed_items_returns_conflict(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex/jobs/"
            "00000000-0000-0000-0000-000000000002/"
            "retry-failed"
        )

    assert response.status_code == 409
