"""EUR-Lex import HTTP endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status,
)

from eke.application.eurlex import EurLexResourceImportService
from eke.domain.identity import CelexIdentifier
from eke.presentation.api.dependencies import (
    get_eurlex_import_service,
)
from eke.presentation.api.mappers import resource_to_response
from eke.presentation.api.schemas import (
    APIErrorResponse,
    EurLexImportRequest,
    EurLexImportResponse,
)

router = APIRouter(
    prefix="/imports/eurlex",
    tags=["eurlex-imports"],
)

EurLexImportServiceDependency = Annotated[
    EurLexResourceImportService,
    Depends(get_eurlex_import_service),
]


@router.post(
    "",
    response_model=EurLexImportResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_201_CREATED: {
            "model": EurLexImportResponse,
            "description": "A new Resource was imported.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": APIErrorResponse,
            "description": "The CELEX identifier was not found upstream.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": APIErrorResponse,
            "description": "EUR-Lex retrieval or metadata parsing failed.",
        },
    },
    summary="Import a Resource from EUR-Lex",
)
def import_eurlex_resource(
    request: EurLexImportRequest,
    service: EurLexImportServiceDependency,
    response: Response,
) -> EurLexImportResponse:
    """Import one Resource by CELEX, idempotently."""
    try:
        celex_identifier = CelexIdentifier.parse(request.celex)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="celex must be a valid standard-form CELEX identifier",
        ) from exc

    result = service.import_resource(celex_identifier)
    resource_response = resource_to_response(result.resource)

    response.status_code = (
        status.HTTP_201_CREATED
        if result.created
        else status.HTTP_200_OK
    )
    response.headers["Location"] = (
        f"/resources/{result.resource.resource_uuid}"
    )

    return EurLexImportResponse(
        created=result.created,
        resource=resource_response,
    )
