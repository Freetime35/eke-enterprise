"""JSON codec for persistent import jobs."""

from __future__ import annotations

from datetime import datetime
from json import dumps, loads
from typing import Any
from uuid import UUID

from eke.domain.imports import ImportJob, ImportJobStatus

IMPORT_JOB_PAYLOAD_VERSION = 1


def encode_import_job(job: ImportJob) -> str:
    """Serialize an ImportJob without losing timezone data."""
    if not isinstance(job, ImportJob):
        raise TypeError("job must be an ImportJob")

    return dumps(
        {
            "job_uuid": str(job.job_uuid),
            "celex": list(job.celex),
            "status": job.status.value,
            "created_at": job.created_at.isoformat(),
            "started_at": (
                job.started_at.isoformat()
                if job.started_at is not None
                else None
            ),
            "completed_at": (
                job.completed_at.isoformat()
                if job.completed_at is not None
                else None
            ),
            "total": job.total,
            "created": job.created,
            "existing": job.existing,
            "failed": job.failed,
            "result_json": job.result_json,
            "error_detail": job.error_detail,
        },
        separators=(",", ":"),
        sort_keys=True,
    )


def decode_import_job(payload: str) -> ImportJob:
    """Deserialize a version-1 ImportJob payload."""
    if not isinstance(payload, str):
        raise TypeError("payload must be a string")
    raw: dict[str, Any] = loads(payload)

    return ImportJob(
        job_uuid=UUID(raw["job_uuid"]),
        celex=tuple(raw["celex"]),
        status=ImportJobStatus(raw["status"]),
        created_at=datetime.fromisoformat(
            raw["created_at"]
        ),
        started_at=_parse_datetime(raw["started_at"]),
        completed_at=_parse_datetime(
            raw["completed_at"]
        ),
        total=raw["total"],
        created=raw["created"],
        existing=raw["existing"],
        failed=raw["failed"],
        result_json=raw["result_json"],
        error_detail=raw["error_detail"],
    )


def _parse_datetime(
    value: str | None,
) -> datetime | None:
    return (
        datetime.fromisoformat(value)
        if value is not None
        else None
    )
