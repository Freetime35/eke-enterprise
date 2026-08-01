"""Pydantic schemas for EUR-Lex import jobs."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from eke.domain.imports import ImportJobStatus


class ImportJobCreateRequest(BaseModel):
    """Request creation of one persistent import job."""

    model_config = ConfigDict(extra="forbid")

    celex: list[str] = Field(
        min_length=1,
        max_length=100,
        examples=[["32023R1114", "32013R0575"]],
    )


class ImportJobResponse(BaseModel):
    """Represent one persistent import job."""

    model_config = ConfigDict(extra="forbid")

    job_uuid: UUID
    status: ImportJobStatus
    celex: list[str]
    total: int
    created: int
    existing: int
    failed: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    retried_from_job_uuid: UUID | None
    results: list[dict[str, Any]] | None
    error_detail: str | None


class ImportJobLineageResponse(BaseModel):
    """Represent one retry chain from root to current job."""

    model_config = ConfigDict(extra="forbid")

    root_job_uuid: UUID
    current_job_uuid: UUID
    depth: int
    items: list[ImportJobResponse]


class ImportJobSearchResponse(BaseModel):
    """Represent one paginated import-job search result."""

    model_config = ConfigDict(extra="forbid")

    items: list[ImportJobResponse]
    total: int
    limit: int
    offset: int


class ImportJobStatusSummaryResponse(BaseModel):
    """Represent aggregate job counts by lifecycle state."""

    model_config = ConfigDict(extra="forbid")

    total: int
    counts: dict[ImportJobStatus, int]


class ImportJobSubmissionResponse(BaseModel):
    """Confirm asynchronous acceptance of an import job."""

    model_config = ConfigDict(extra="forbid")

    job_uuid: UUID
    accepted: bool
    location: str
