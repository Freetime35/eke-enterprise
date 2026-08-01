"""API tests for bulk EUR-Lex imports."""

from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    EurLexBulkImportItem,
    EurLexBulkImportResult,
    EurLexBulkImportStatus,
)
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_eurlex_bulk_import_service,
)


class FakeBulkService:
    def import_resources(self, identifiers):
        return EurLexBulkImportResult(
            (
                EurLexBulkImportItem(
                    celex=identifiers[0].value,
                    status=EurLexBulkImportStatus.CREATED,
                    resource_uuid=(
                        "00000000-0000-0000-0000-000000000001"
                    ),
                ),
                EurLexBulkImportItem(
                    celex=identifiers[1].value,
                    status=EurLexBulkImportStatus.FAILED,
                    error_code="eurlex_client_error",
                    detail="not found",
                ),
            )
        )


def make_client(tmp_path: Path) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'bulk-import.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_eurlex_bulk_import_service
    ] = lambda: FakeBulkService()
    return TestClient(app)


def test_bulk_import_returns_summary(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/imports/eurlex/bulk",
            json={
                "celex": [
                    "32023R1114",
                    "32013R0575",
                ]
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["created"] == 1
    assert response.json()["failed"] == 1


def test_bulk_import_rejects_invalid_item(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/imports/eurlex/bulk",
            json={"celex": ["32023R1114", "invalid"]},
        )

    assert response.status_code == 422
    assert response.json()["detail"]["index"] == 1
