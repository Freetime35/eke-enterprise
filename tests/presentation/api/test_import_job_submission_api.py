"""API tests for asynchronous import-job submission."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    ImportJobNotFoundError,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.imports import ImportJob
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_import_job_service,
    get_import_job_worker,
)

NOW = datetime(2026, 8, 2, 12, 0, tzinfo=UTC)


class FakeImportJobService:
    def __init__(self) -> None:
        self.jobs: dict[UUID, ImportJob] = {}

    def create_job(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> ImportJob:
        job = ImportJob.create(
            tuple(
                identifier.value
                for identifier in identifiers
            ),
            created_at=NOW,
        )
        self.jobs[job.job_uuid] = job
        return job

    def get_job(self, job_uuid: UUID) -> ImportJob:
        job = self.jobs.get(job_uuid)
        if job is None:
            raise ImportJobNotFoundError(
                f"import job not found: {job_uuid}"
            )
        return job


class FakeWorker:
    def __init__(self) -> None:
        self.submissions: list[UUID] = []
        self.accept = True

    def submit(self, job_uuid: UUID) -> bool:
        if not self.accept:
            return False
        self.submissions.append(job_uuid)
        return True

    def shutdown(self, *, wait: bool = True) -> None:
        del wait


def make_client(
    tmp_path: Path,
    service: FakeImportJobService,
    worker: FakeWorker,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'job-submission.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    app.dependency_overrides[
        get_import_job_worker
    ] = lambda: worker
    return TestClient(app)


def test_submit_job_returns_202(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()
    worker = FakeWorker()

    with make_client(tmp_path, service, worker) as client:
        created = client.post(
            "/imports/eurlex/jobs",
            json={"celex": ["32023R1114"]},
        )
        job_uuid = created.json()["job_uuid"]

        submitted = client.post(
            f"/imports/eurlex/jobs/{job_uuid}/submit"
        )

    assert submitted.status_code == 202
    assert submitted.json() == {
        "job_uuid": job_uuid,
        "accepted": True,
        "location": f"/imports/eurlex/jobs/{job_uuid}",
    }
    assert worker.submissions == [UUID(job_uuid)]


def test_duplicate_submission_returns_409(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()
    worker = FakeWorker()
    worker.accept = False

    with make_client(tmp_path, service, worker) as client:
        created = client.post(
            "/imports/eurlex/jobs",
            json={"celex": ["32023R1114"]},
        )
        job_uuid = created.json()["job_uuid"]

        response = client.post(
            f"/imports/eurlex/jobs/{job_uuid}/submit"
        )

    assert response.status_code == 409


def test_missing_job_submission_returns_404(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()
    worker = FakeWorker()

    with make_client(tmp_path, service, worker) as client:
        response = client.post(
            "/imports/eurlex/jobs/"
            "00000000-0000-0000-0000-000000000001/"
            "submit"
        )

    assert response.status_code == 404
    assert worker.submissions == []
