"""API tests for import-job retry."""

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobNotFoundError,
    ImportJobStateError,
)
from eke.domain.imports import ImportJob, ImportJobStatus
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeService:
    def __init__(self) -> None:
        failed = ImportJob.create(
            ("32023R1114",),
            created_at=NOW,
        )
        failed = replace(
            failed,
            status=ImportJobStatus.FAILED,
        )
        self.jobs = {failed.job_uuid: failed}
        self.failed_uuid = failed.job_uuid

    def retry_job(self, job_uuid: UUID) -> ImportJob:
        job = self.jobs.get(job_uuid)
        if job is None:
            raise ImportJobNotFoundError("import job not found")
        if job.status is not ImportJobStatus.FAILED:
            raise ImportJobStateError("job cannot be retried")

        retried = ImportJob.create(
            job.celex,
            created_at=NOW,
            retried_from_job_uuid=job.job_uuid,
        )
        self.jobs[retried.job_uuid] = retried
        return retried


def make_client(
    tmp_path: Path,
    service: FakeService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'job-retry.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_retry_job_returns_created(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            f"/imports/eurlex/jobs/"
            f"{service.failed_uuid}/retry"
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["retried_from_job_uuid"] == (
        str(service.failed_uuid)
    )
    assert response.headers["location"] == (
        f"/imports/eurlex/jobs/{body['job_uuid']}"
    )


def test_retry_missing_job_returns_404(
    tmp_path: Path,
) -> None:
    service = FakeService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex/jobs/"
            "00000000-0000-0000-0000-000000000001/"
            "retry"
        )

    assert response.status_code == 404
