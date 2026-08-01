"""Integration tests for EUR-Lex import-job endpoints."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from json import dumps
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

NOW = datetime(2026, 8, 2, 8, 0, tzinfo=UTC)


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

    def run_job(self, job_uuid: UUID) -> ImportJob:
        job = self.get_job(job_uuid)
        if job.status is not ImportJobStatus.PENDING:
            raise ImportJobStateError(
                "only pending import jobs can be run"
            )

        completed = replace(
            job,
            status=ImportJobStatus.COMPLETED,
            started_at=NOW,
            completed_at=NOW,
            created=job.total,
            result_json=dumps(
                [
                    {
                        "celex": value,
                        "status": "CREATED",
                        "resource_uuid": (
                            "00000000-0000-0000-"
                            "0000-000000000001"
                        ),
                        "error_code": None,
                        "detail": None,
                    }
                    for value in job.celex
                ]
            ),
        )
        self.jobs[job_uuid] = completed
        return completed


def make_client(
    tmp_path: Path,
    service: FakeImportJobService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'import-jobs-api.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_import_job_service
    ] = lambda: service
    return TestClient(app)


def test_create_get_and_run_import_job(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()

    with make_client(tmp_path, service) as client:
        created = client.post(
            "/imports/eurlex/jobs",
            json={
                "celex": [
                    "32023R1114",
                    "32013R0575",
                ]
            },
        )
        job_uuid = created.json()["job_uuid"]

        fetched = client.get(
            f"/imports/eurlex/jobs/{job_uuid}"
        )
        completed = client.post(
            f"/imports/eurlex/jobs/{job_uuid}/run"
        )

    assert created.status_code == 201
    assert created.headers["location"] == (
        f"/imports/eurlex/jobs/{job_uuid}"
    )
    assert created.json()["status"] == "PENDING"
    assert fetched.status_code == 200
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"
    assert completed.json()["created"] == 2
    assert len(completed.json()["results"]) == 2


def test_create_job_rejects_invalid_celex(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex/jobs",
            json={
                "celex": [
                    "32023R1114",
                    "invalid",
                ]
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"]["index"] == 1


def test_missing_job_returns_404(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()

    with make_client(tmp_path, service) as client:
        response = client.get(
            "/imports/eurlex/jobs/"
            "00000000-0000-0000-0000-000000000001"
        )

    assert response.status_code == 404


def test_completed_job_cannot_run_again(
    tmp_path: Path,
) -> None:
    service = FakeImportJobService()

    with make_client(tmp_path, service) as client:
        created = client.post(
            "/imports/eurlex/jobs",
            json={"celex": ["32023R1114"]},
        )
        job_uuid = created.json()["job_uuid"]
        first = client.post(
            f"/imports/eurlex/jobs/{job_uuid}/run"
        )
        second = client.post(
            f"/imports/eurlex/jobs/{job_uuid}/run"
        )

    assert first.status_code == 200
    assert second.status_code == 409
