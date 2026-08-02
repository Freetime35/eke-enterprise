"""API tests for import-job result item inspection."""

from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    EurLexBulkImportStatus,
)
from eke.application.eurlex.import_job_results import (
    ImportJobResultItem,
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

    def get_result_items(
        self,
        job_uuid: UUID,
        *,
        item_status: (
            EurLexBulkImportStatus | None
        ) = None,
    ) -> tuple[ImportJobResultItem, ...]:
        items = (
            ImportJobResultItem(
                celex="32023R1114",
                status=EurLexBulkImportStatus.CREATED,
                resource_uuid="resource-1",
                error_code=None,
                detail=None,
            ),
            ImportJobResultItem(
                celex="32024R0001",
                status=EurLexBulkImportStatus.FAILED,
                resource_uuid=None,
                error_code="INVALID_METADATA",
                detail="missing resource type",
            ),
        )
        if item_status is None:
            return items
        return tuple(
            item
            for item in items
            if item.status is item_status
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
                f"{tmp_path / 'result-items.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_get_import_job_result_items(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            f"/imports/eurlex/jobs/"
            f"{service.job_uuid}/items",
            params={"status": "FAILED"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["items"][0]["status"] == "FAILED"
    assert (
        body["items"][0]["error_code"]
        == "INVALID_METADATA"
    )
