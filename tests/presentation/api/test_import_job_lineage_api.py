"""API tests for import-job retry lineage."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import ImportJobLineage
from eke.domain.imports import ImportJob
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeService:
    def __init__(self) -> None:
        self.root = ImportJob.create(
            ("32023R1114",),
            created_at=NOW,
        )
        self.current = ImportJob.create(
            self.root.celex,
            created_at=NOW,
            retried_from_job_uuid=self.root.job_uuid,
        )

    def get_job_lineage(
        self,
        job_uuid: UUID,
    ) -> ImportJobLineage:
        assert job_uuid == self.current.job_uuid
        return ImportJobLineage(
            items=(self.root, self.current)
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
                f"{tmp_path / 'job-lineage.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_job_lineage(tmp_path: Path) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            f"/imports/eurlex/jobs/"
            f"{service.current.job_uuid}/lineage"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["root_job_uuid"] == str(
        service.root.job_uuid
    )
    assert body["current_job_uuid"] == str(
        service.current.job_uuid
    )
    assert body["depth"] == 1
    assert len(body["items"]) == 2
