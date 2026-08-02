"""API tests for import-job result summaries."""

from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    EurLexBulkImportStatus,
)
from eke.application.eurlex.import_job_result_summary import (
    ImportJobResultSummary,
)
from eke.presentation.api import (
    APISettings,
    create_app,
)
from eke.presentation.api.dependencies import (
    get_import_job_service,
)


class FakeService:
    def __init__(self) -> None:
        self.job_uuid = UUID(
            "00000000-0000-0000-0000-000000000001"
        )

    def get_result_summary(
        self,
        job_uuid: UUID,
    ) -> ImportJobResultSummary:
        assert job_uuid == self.job_uuid

        return ImportJobResultSummary(
            total=4,
            counts={
                EurLexBulkImportStatus.CREATED: 2,
                EurLexBulkImportStatus.EXISTING: 1,
                EurLexBulkImportStatus.FAILED: 1,
            },
            success_count=3,
            failure_count=1,
            success_rate=0.75,
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
                f"{tmp_path / 'result-summary.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_import_job_result_summary(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            f"/imports/eurlex/jobs/"
            f"{service.job_uuid}/items/summary"
        )

    assert response.status_code == 200
    assert response.json() == {
        "job_uuid": str(service.job_uuid),
        "total": 4,
        "counts": {
            "CREATED": 2,
            "EXISTING": 1,
            "FAILED": 1,
        },
        "success_count": 3,
        "failure_count": 1,
        "success_rate": 0.75,
        "failure_rate": 0.25,
    }
