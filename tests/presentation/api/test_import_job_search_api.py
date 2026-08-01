"""API tests for import-job listing and filtering."""

from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobSearchCriteria,
    ImportJobSearchPage,
)
from eke.domain.imports import ImportJob, ImportJobStatus
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeSearchService:
    def __init__(self) -> None:
        self.criteria: ImportJobSearchCriteria | None = None

    def search_jobs(
        self,
        criteria: ImportJobSearchCriteria,
    ) -> ImportJobSearchPage:
        self.criteria = criteria
        job = ImportJob.create(
            ("32023R1114",),
            created_at=NOW,
        )
        return ImportJobSearchPage(
            items=(job,),
            total=1,
            limit=criteria.limit,
            offset=criteria.offset,
        )


def make_client(
    tmp_path: Path,
    service: FakeSearchService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'job-search.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_search_jobs_returns_page(
    tmp_path: Path,
) -> None:
    service = FakeSearchService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            "/imports/eurlex/jobs",
            params={
                "status": "PENDING",
                "limit": 10,
                "offset": 20,
            },
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["limit"] == 10
    assert response.json()["offset"] == 20
    assert response.json()["items"][0]["status"] == (
        "PENDING"
    )
    assert service.criteria is not None
    assert (
        service.criteria.status
        is ImportJobStatus.PENDING
    )


def test_search_jobs_rejects_invalid_date_window(
    tmp_path: Path,
) -> None:
    service = FakeSearchService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            "/imports/eurlex/jobs",
            params={
                "created_from": (
                    "2026-08-02T00:00:00+00:00"
                ),
                "created_to": (
                    "2026-08-01T00:00:00+00:00"
                ),
            },
        )

    assert response.status_code == 422
