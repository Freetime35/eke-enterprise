"""EUR-Lex import job HTTP endpoints."""

from __future__ import annotations

from json import loads
from typing import Annotated, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from eke.application.eurlex import (
    EurLexImportJobService,
    ImportJobNotFoundError,
    ImportJobStateError,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.imports import ImportJob
from eke.presentation.api.dependencies import (
    get_import_job_service,
)
from eke.presentation.api.schemas import (
    APIErrorResponse,
    ImportJobCreateRequest,
    ImportJobResponse,
)

router = APIRouter(
    prefix="/imports/eurlex/jobs",
    tags=["eurlex-import-jobs"],
)

ImportJobServiceDependency = Annotated[
    EurLexImportJobService,
    Depends(get_import_job_service),
]


@router.post(
    "",
    response_model=ImportJobResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": APIErrorResponse,
            "description": "At least one CELEX value is invalid.",
        },
    },
    summary="Create an EUR-Lex import job",
)
def create_import_job(
    request: ImportJobCreateRequest,
    service: ImportJobServiceDependency,
    response: Response,
) -> ImportJobResponse:
    """Create and persist a pending import job."""
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
                    "message": (
                        "celex must be a valid standard-form "
                        "CELEX identifier"
                    ),
                },
            ) from exc

    job = service.create_job(tuple(identifiers))
    response.headers["Location"] = (
        f"/imports/eurlex/jobs/{job.job_uuid}"
    )
    return _to_response(job)


@router.get(
    "/{job_uuid}",
    response_model=ImportJobResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": APIErrorResponse,
            "description": "The import job does not exist.",
        },
    },
    summary="Get an EUR-Lex import job",
)
def get_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
) -> ImportJobResponse:
    """Return one import job by UUID."""
    try:
        job = service.get_job(job_uuid)
    except ImportJobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return _to_response(job)


@router.post(
    "/{job_uuid}/run",
    response_model=ImportJobResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": APIErrorResponse,
            "description": "The import job does not exist.",
        },
        status.HTTP_409_CONFLICT: {
            "model": APIErrorResponse,
            "description": "The import job cannot be run.",
        },
    },
    summary="Run an EUR-Lex import job",
)
def run_import_job(
    job_uuid: UUID,
    service: ImportJobServiceDependency,
) -> ImportJobResponse:
    """Run one pending import job synchronously."""
    try:
        job = service.run_job(job_uuid)
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

    return _to_response(job)


def _to_response(job: ImportJob) -> ImportJobResponse:
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
        results=results,
        error_detail=job.error_detail,
    )
