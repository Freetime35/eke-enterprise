"""EUR-Lex import job HTTP endpoints."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from json import loads
from typing import Annotated, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)

from eke.application.eurlex import (
    EurLexImportJobService,
    ImportJobLineageError,
    ImportJobNotFoundError,
    ImportJobSearchCriteria,
    ImportJobStateError,
    ImportJobWorker,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.imports import ImportJob, ImportJobStatus
from eke.presentation.api.dependencies import (
    get_import_job_service,
    get_import_job_worker,
)
from eke.presentation.api.schemas import (
    ImportJobCreateRequest,
    ImportJobDurationStatisticsResponse,
    ImportJobLineageResponse,
    ImportJobOperationalMetricsResponse,
    ImportJobResponse,
    ImportJobSearchResponse,
    ImportJobStatusSummaryResponse,
    ImportJobSubmissionResponse,
    StaleImportJobReportResponse,
    StaleImportJobResponse,
)

router = APIRouter(
    prefix="/imports/eurlex/jobs",
    tags=["eurlex-import-jobs"],
)

ImportJobServiceDependency = Annotated[
    EurLexImportJobService,
    Depends(get_import_job_service),
]
ImportJobWorkerDependency = Annotated[
    ImportJobWorker,
    Depends(get_import_job_worker),
]


@router.post(
    "",
    response_model=ImportJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_import_job(
    request: ImportJobCreateRequest,
    service: ImportJobServiceDependency,
    response: Response,
) -> ImportJobResponse:
    identifiers: list[CelexIdentifier] = []

    for index, value in enumerate(request.celex):
        try:
            identifiers.append(
                CelexIdentifier.parse(value)
            )
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=(
                    status.HTTP_422_UNPROCESSABLE_CONTENT
                ),
                detail={
                    "index": index,
                    "celex": value,
                    "message": "invalid CELEX identifier",
                },
            ) from exc

    job = service.create_job(tuple(identifiers))
    response.headers["Location"] = (
        f"/imports/eurlex/jobs/{job.job_uuid}"
    )

    return _to_response(job)


@router.get(
    "",
    response_model=ImportJobSearchResponse,
)
def search_import_jobs(
    service: ImportJobServiceDependency,
    job_status: Annotated[
        ImportJobStatus | None,
        Query(alias="status"),
    ] = None,
    created_from: Annotated[
        datetime | None,
        Query(),
    ] = None,
    created_to: Annotated[
        datetime | None,
        Query(),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> ImportJobSearchResponse:
    try:
        criteria = ImportJobSearchCriteria(
            status=job_status,
            created_from=created_from,
            created_to=created_to,
            limit=limit,
            offset=offset,
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_CONTENT
            ),
            detail=str(exc),
        ) from exc

    page = service.search_jobs(criteria)

    return ImportJobSearchResponse(
        items=[
            _to_response(item)
            for item in page.items
        ],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get(
    "/summary",
    response_model=ImportJobStatusSummaryResponse,
)
def summarize_import_jobs(
    service: ImportJobServiceDependency,
) -> ImportJobStatusSummaryResponse:
    summary = service.summarize_jobs()

    return ImportJobStatusSummaryResponse(
        total=summary.total,
        counts=summary.counts,
    )


@router.get(
    "/metrics",
    response_model=ImportJobOperationalMetricsResponse,
)
def get_import_job_metrics(
    service: ImportJobServiceDependency,
) -> ImportJobOperationalMetricsResponse:
    metrics = service.get_operational_metrics()

    return ImportJobOperationalMetricsResponse(
        total=metrics.total,
        active=metrics.active,
        terminal=metrics.terminal,
        successful=metrics.successful,
        unsuccessful=metrics.unsuccessful,
        cancelled=metrics.cancelled,
        completion_rate=metrics.completion_rate,
        failure_rate=metrics.failure_rate,
    )


@router.get(
    "/durations",
    response_model=ImportJobDurationStatisticsResponse,
    summary="Get EUR-Lex import job duration statistics",
)
def get_import_job_duration_statistics(
    service: ImportJobServiceDependency,
) -> ImportJobDurationStatisticsResponse:
    """Return duration statistics for completed executions."""
    statistics = service.get_duration_statistics()

    return ImportJobDurationStatisticsResponse(
        sample_count=statistics.sample_count,
        minimum_seconds=statistics.minimum_seconds,
        maximum_seconds=statistics.maximum_seconds,
        average_seconds=statistics.average_seconds,
    )


@router.get(
    "/stale",
    response_model=StaleImportJobReportResponse,
    summary="Get stale EUR-Lex import jobs",
)
def get_stale_import_jobs(
    service: ImportJobServiceDependency,
    threshold_seconds: Annotated[
        int,
        Query(ge=1, le=604800),
    ] = 3600,
) -> StaleImportJobReportResponse:
    """Return running jobs older than the threshold."""
    report = service.get_stale_jobs(
        threshold_seconds=threshold_seconds
    )

    return StaleImportJobReportResponse(
        threshold_seconds=report.threshold_seconds,
        observed_at=report.observed_at,
        count=len(report.items),
        items=[
            StaleImportJobResponse(
                job=_to_response(item.job),
                age_seconds=item.age_seconds,
            )
            for item in report.items
        ],
    )


@router.get(
    "/{job_uuid}",
    response_model=ImportJobResponse,
)
def get_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
) -> ImportJobResponse:
    return _to_response(
        _get_job(service, job_uuid)
    )


@router.get(
    "/{job_uuid}/lineage",
    response_model=ImportJobLineageResponse,
)
def get_import_job_lineage(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
) -> ImportJobLineageResponse:
    try:
        lineage = service.get_job_lineage(job_uuid)
    except ImportJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ImportJobLineageError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return ImportJobLineageResponse(
        root_job_uuid=lineage.root.job_uuid,
        current_job_uuid=lineage.current.job_uuid,
        depth=lineage.depth,
        items=[
            _to_response(item)
            for item in lineage.items
        ],
    )


@router.post(
    "/{job_uuid}/run",
    response_model=ImportJobResponse,
)
def run_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
) -> ImportJobResponse:
    return _transition(
        service.run_job,
        job_uuid,
    )


@router.post(
    "/{job_uuid}/cancel",
    response_model=ImportJobResponse,
)
def cancel_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
) -> ImportJobResponse:
    return _transition(
        service.cancel_job,
        job_uuid,
    )


@router.post(
    "/{job_uuid}/retry",
    response_model=ImportJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def retry_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
    response: Response,
) -> ImportJobResponse:
    retried = _transition(
        service.retry_job,
        job_uuid,
    )

    response.headers["Location"] = (
        f"/imports/eurlex/jobs/{retried.job_uuid}"
    )

    return retried


@router.post(
    "/{job_uuid}/recover-stale",
    response_model=ImportJobResponse,
    summary="Recover a stale EUR-Lex import job",
)
def recover_stale_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
    threshold_seconds: Annotated[
        int,
        Query(ge=1, le=604800),
    ] = 3600,
) -> ImportJobResponse:
    """Mark one stale running job as failed."""
    try:
        recovered = service.recover_stale_job(
            job_uuid,
            threshold_seconds=threshold_seconds,
        )
    except ImportJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ImportJobStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _to_response(recovered)


@router.post(
    "/{job_uuid}/submit",
    response_model=ImportJobSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def submit_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
    worker: ImportJobWorkerDependency,
) -> ImportJobSubmissionResponse:
    job = _get_job(service, job_uuid)

    if job.status is not ImportJobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "only pending import jobs can be submitted"
            ),
        )

    if not worker.submit(job_uuid):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="import job is already submitted",
        )

    location = f"/imports/eurlex/jobs/{job_uuid}"

    return ImportJobSubmissionResponse(
        job_uuid=job_uuid,
        accepted=True,
        location=location,
    )


def _transition(
    transition: Callable[[UUID], ImportJob],
    job_uuid: UUID,
) -> ImportJobResponse:
    try:
        return _to_response(
            transition(job_uuid)
        )
    except ImportJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ImportJobStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


def _get_job(
    service: EurLexImportJobService,
    job_uuid: UUID,
) -> ImportJob:
    try:
        return service.get_job(job_uuid)
    except ImportJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


def _to_response(
    job: ImportJob,
) -> ImportJobResponse:
    results: list[dict[str, Any]] | None = None

    if job.result_json is not None:
        parsed = loads(job.result_json)

        if isinstance(parsed, list):
            results = [
                item
                for item in parsed
                if isinstance(item, dict)
            ]

    return ImportJobResponse(
        job_uuid=job.job_uuid,
        status=job.status,
        celex=list(job.celex),
        total=job.total,
        created=job.created,
        existing=job.existing,
        failed=job.failed,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        cancelled_at=job.cancelled_at,
        retried_from_job_uuid=job.retried_from_job_uuid,
        results=results,
        error_detail=job.error_detail,
    )