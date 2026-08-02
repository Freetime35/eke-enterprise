"""API tests for failed import-item inspection."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import ImportJobStateError
from eke.application.eurlex.import_job_failed_items import (
    FailedImportItem,
)
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeService:
    def __init__(self) -> None:
        self.job_uuid = UUID(
            "00000000-0000-0000-0000-000000000001"
        )

    def get_failed_items(
        self,
        job_uuid: UUID,
    ) -> tuple[FailedImportItem, ...]:
        if job_uuid != self.job_uuid:
            raise ImportJobStateError(
                "import job has no failed items"
            )

        return (
            FailedImportItem(
                celex="32024R0001",
                error_code="INVALID_METADATA",
                detail="missing resource type",
            ),
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
                f"{tmp_path / 'failed-items.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service

    return TestClient(app)


def test_get_failed_import_items(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            f"/imports/eurlex/jobs/"
            f"{service.job_uuid}/failed-items"
        )

    assert response.status_code == 200
    assert response.json() == {
        "job_uuid": str(service.job_uuid),
        "count": 1,
        "items": [
            {
                "celex": "32024R0001",
                "error_code": "INVALID_METADATA",
                "detail": "missing resource type",
            }
        ],
    }


def test_get_failed_import_items_returns_conflict(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            "/imports/eurlex/jobs/"
            "00000000-0000-0000-0000-000000000002/"
            "failed-items"
        )

    assert response.status_code == 409
