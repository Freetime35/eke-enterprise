"""Pydantic schemas for EUR-Lex import jobs."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from eke.application.eurlex import EurLexBulkImportStatus
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



class ImportJobResultItemResponse(BaseModel):
    """Represent one persisted import result item."""

    model_config = ConfigDict(extra="forbid")

    celex: str
    status: EurLexBulkImportStatus
    resource_uuid: str | None
    error_code: str | None
    detail: str | None


class ImportJobResultItemsResponse(BaseModel):
    """Represent item-level results for one import job."""

    model_config = ConfigDict(extra="forbid")

    job_uuid: UUID
    count: int
    items: list[ImportJobResultItemResponse]



class ImportJobResultSummaryResponse(BaseModel):
    """Represent aggregate item-level outcomes for one job."""

    model_config = ConfigDict(extra="forbid")

    job_uuid: UUID
    total: int
    counts: dict[EurLexBulkImportStatus, int]
    success_count: int
    failure_count: int
    success_rate: float
    failure_rate: float


class FailedImportItemResponse(BaseModel):
    """Represent one failed import result item."""

    model_config = ConfigDict(extra="forbid")

    celex: str
    error_code: str | None
    detail: str | None


class FailedImportItemsResponse(BaseModel):
    """Represent all failed items for one import job."""

    model_config = ConfigDict(extra="forbid")

    job_uuid: UUID
    count: int
    items: list[FailedImportItemResponse]


class StaleImportJobResponse(BaseModel):
    """Represent one stale running import job."""

    model_config = ConfigDict(extra="forbid")

    job: ImportJobResponse
    age_seconds: float


class StaleImportJobReportResponse(BaseModel):
    """Represent stale jobs for one threshold."""

    model_config = ConfigDict(extra="forbid")

    threshold_seconds: int
    observed_at: datetime
    count: int
    items: list[StaleImportJobResponse]


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


class ImportJobOperationalMetricsResponse(BaseModel):
    """Represent derived operational import-job indicators."""

    model_config = ConfigDict(extra="forbid")

    total: int
    active: int
    terminal: int
    successful: int
    unsuccessful: int
    cancelled: int
    completion_rate: float
    failure_rate: float


class ImportJobDurationStatisticsResponse(BaseModel):
    """Represent aggregate execution-duration statistics."""

    model_config = ConfigDict(extra="forbid")

    sample_count: int
    minimum_seconds: float | None
    maximum_seconds: float | None
    average_seconds: float | None


class ImportJobSubmissionResponse(BaseModel):
    """Confirm asynchronous acceptance of an import job."""

    model_config = ConfigDict(extra="forbid")

    job_uuid: UUID
    accepted: bool
    location: str
