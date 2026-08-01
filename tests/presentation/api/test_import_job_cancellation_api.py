"""API tests for import-job cancellation."""

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobNotFoundError,
    ImportJobStateError,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.imports import ImportJob, ImportJobStatus
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeService:
    def __init__(self) -> None:
        self.jobs: dict[UUID, ImportJob] = {}

    def create_job(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> ImportJob:
        job = ImportJob.create(
            tuple(item.value for item in identifiers),
            created_at=NOW,
        )
        self.jobs[job.job_uuid] = job
        return job

    def cancel_job(self, job_uuid: UUID) -> ImportJob:
        job = self.jobs.get(job_uuid)
        if job is None:
            raise ImportJobNotFoundError("import job not found")
        if job.status is not ImportJobStatus.PENDING:
            raise ImportJobStateError(
                "only pending import jobs can be cancelled"
            )
        cancelled = replace(
            job,
            status=ImportJobStatus.CANCELLED,
            cancelled_at=NOW,
        )
        self.jobs[job_uuid] = cancelled
        return cancelled


def make_client(
    tmp_path: Path,
    service: FakeService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'job-cancel.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_cancel_pending_job(tmp_path: Path) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        created = client.post(
            "/imports/eurlex/jobs",
            json={"celex": ["32023R1114"]},
        )
        job_uuid = created.json()["job_uuid"]
        response = client.post(
            f"/imports/eurlex/jobs/{job_uuid}/cancel"
        )

    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
    assert response.json()["cancelled_at"] is not None


def test_cancel_missing_job_returns_404(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex/jobs/"
            "00000000-0000-0000-0000-000000000001/"
            "cancel"
        )

    assert response.status_code == 404
