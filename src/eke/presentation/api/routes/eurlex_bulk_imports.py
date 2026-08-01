"""Bulk EUR-Lex import HTTP endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from eke.application.eurlex import EurLexBulkImportService
from eke.domain.identity import CelexIdentifier
from eke.presentation.api.dependencies import (
    get_eurlex_bulk_import_service,
)
from eke.presentation.api.schemas.eurlex_bulk_imports import (
    EurLexBulkImportItemResponse,
    EurLexBulkImportRequest,
    EurLexBulkImportResponse,
)

router = APIRouter(
    prefix="/imports/eurlex/bulk",
    tags=["eurlex-imports"],
)

BulkImportServiceDependency = Annotated[
    EurLexBulkImportService,
    Depends(get_eurlex_bulk_import_service),
]


@router.post(
    "",
    response_model=EurLexBulkImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Import multiple Resources from EUR-Lex",
)
def bulk_import_eurlex_resources(
    request: EurLexBulkImportRequest,
    service: BulkImportServiceDependency,
) -> EurLexBulkImportResponse:
    """Import unique CELEX values independently."""
    parsed: list[CelexIdentifier] = []

    for index, value in enumerate(request.celex):
        try:
            parsed.append(CelexIdentifier.parse(value))
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

    result = service.import_resources(tuple(parsed))

    return EurLexBulkImportResponse(
        total=result.total,
        created=result.created,
        existing=result.existing,
        failed=result.failed,
        items=[
            EurLexBulkImportItemResponse(
                celex=item.celex,
                status=item.status,
                resource_uuid=item.resource_uuid,
                error_code=item.error_code,
                detail=item.detail,
            )
            for item in result.items
        ],
    )
