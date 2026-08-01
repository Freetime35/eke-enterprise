"""HTTP exception mapping for application errors."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from eke.application.eurlex import (
    EurLexDocumentNotFoundError,
    EurLexMetadataError,
    EurLexUpstreamError,
)
from eke.application.resources import (
    ProvenanceRecordAlreadyExistsError,
    ProvenanceRecordConflictError,
    ProvenanceRecordNotFoundError,
    ResourceAlreadyExistsError,
    ResourceClassificationAlreadyExistsError,
    ResourceClassificationNotFoundError,
    ResourceNotFoundError,
    ResourceRelationshipAlreadyExistsError,
    ResourceRelationshipConflictError,
    ResourceRelationshipNotFoundError,
    ResourceTitleAlreadyExistsError,
    ResourceTitleNotFoundError,
    ResourceVersionAlreadyExistsError,
    ResourceVersionConflictError,
    ResourceVersionNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register stable application-to-HTTP error mappings."""

    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(
        _request: Request,
        exception: ResourceNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "resource_not_found",
            exception,
        )

    @app.exception_handler(ResourceAlreadyExistsError)
    async def resource_conflict_handler(
        _request: Request,
        exception: ResourceAlreadyExistsError,
    ) -> JSONResponse:
        return _error_response(
            409,
            "resource_conflict",
            exception,
        )

    @app.exception_handler(ResourceTitleAlreadyExistsError)
    async def title_conflict_handler(
        _request: Request,
        exception: ResourceTitleAlreadyExistsError,
    ) -> JSONResponse:
        return _error_response(
            409,
            "resource_title_conflict",
            exception,
        )

    @app.exception_handler(ResourceTitleNotFoundError)
    async def title_not_found_handler(
        _request: Request,
        exception: ResourceTitleNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "resource_title_not_found",
            exception,
        )

    @app.exception_handler(ResourceVersionAlreadyExistsError)
    @app.exception_handler(ResourceVersionConflictError)
    async def version_conflict_handler(
        _request: Request,
        exception: Exception,
    ) -> JSONResponse:
        return _error_response(
            409,
            "resource_version_conflict",
            exception,
        )

    @app.exception_handler(ResourceVersionNotFoundError)
    async def version_not_found_handler(
        _request: Request,
        exception: ResourceVersionNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "resource_version_not_found",
            exception,
        )

    @app.exception_handler(
        ResourceRelationshipAlreadyExistsError
    )
    @app.exception_handler(ResourceRelationshipConflictError)
    async def relationship_conflict_handler(
        _request: Request,
        exception: Exception,
    ) -> JSONResponse:
        return _error_response(
            409,
            "resource_relationship_conflict",
            exception,
        )

    @app.exception_handler(ResourceRelationshipNotFoundError)
    async def relationship_not_found_handler(
        _request: Request,
        exception: ResourceRelationshipNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "resource_relationship_not_found",
            exception,
        )

    @app.exception_handler(ProvenanceRecordAlreadyExistsError)
    @app.exception_handler(ProvenanceRecordConflictError)
    async def provenance_conflict_handler(
        _request: Request,
        exception: Exception,
    ) -> JSONResponse:
        return _error_response(
            409,
            "provenance_record_conflict",
            exception,
        )

    @app.exception_handler(ProvenanceRecordNotFoundError)
    async def provenance_not_found_handler(
        _request: Request,
        exception: ProvenanceRecordNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "provenance_record_not_found",
            exception,
        )

    @app.exception_handler(
        ResourceClassificationAlreadyExistsError
    )
    async def classification_conflict_handler(
        _request: Request,
        exception: ResourceClassificationAlreadyExistsError,
    ) -> JSONResponse:
        return _error_response(
            409,
            "resource_classification_conflict",
            exception,
        )

    @app.exception_handler(ResourceClassificationNotFoundError)
    async def classification_not_found_handler(
        _request: Request,
        exception: ResourceClassificationNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "resource_classification_not_found",
            exception,
        )

    @app.exception_handler(EurLexDocumentNotFoundError)
    async def eurlex_not_found_handler(
        _request: Request,
        exception: EurLexDocumentNotFoundError,
    ) -> JSONResponse:
        return _error_response(
            404,
            "eurlex_document_not_found",
            exception,
        )

    @app.exception_handler(EurLexUpstreamError)
    async def eurlex_upstream_handler(
        _request: Request,
        exception: EurLexUpstreamError,
    ) -> JSONResponse:
        return _error_response(
            502,
            "eurlex_upstream_error",
            exception,
        )

    @app.exception_handler(EurLexMetadataError)
    async def eurlex_metadata_handler(
        _request: Request,
        exception: EurLexMetadataError,
    ) -> JSONResponse:
        return _error_response(
            502,
            "eurlex_metadata_error",
            exception,
        )


def _error_response(
    status_code: int,
    code: str,
    exception: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "detail": str(exception),
        },
    )
