"""HTTP exception mapping for application errors."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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
    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_handler(
        _request: Request,
        exception: ResourceNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "resource_not_found",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceAlreadyExistsError)
    async def resource_conflict_handler(
        _request: Request,
        exception: ResourceAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceTitleAlreadyExistsError)
    async def title_conflict_handler(
        _request: Request,
        exception: ResourceTitleAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_title_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceTitleNotFoundError)
    async def title_not_found_handler(
        _request: Request,
        exception: ResourceTitleNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "resource_title_not_found",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceVersionAlreadyExistsError)
    async def version_exists_handler(
        _request: Request,
        exception: ResourceVersionAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_version_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceVersionConflictError)
    async def version_conflict_handler(
        _request: Request,
        exception: ResourceVersionConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_version_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceVersionNotFoundError)
    async def version_not_found_handler(
        _request: Request,
        exception: ResourceVersionNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "resource_version_not_found",
                "detail": str(exception),
            },
        )

    @app.exception_handler(
        ResourceRelationshipAlreadyExistsError
    )
    async def relationship_exists_handler(
        _request: Request,
        exception: ResourceRelationshipAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_relationship_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceRelationshipConflictError)
    async def relationship_conflict_handler(
        _request: Request,
        exception: ResourceRelationshipConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_relationship_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceRelationshipNotFoundError)
    async def relationship_not_found_handler(
        _request: Request,
        exception: ResourceRelationshipNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "resource_relationship_not_found",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ProvenanceRecordAlreadyExistsError)
    async def provenance_exists_handler(
        _request: Request,
        exception: ProvenanceRecordAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "provenance_record_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ProvenanceRecordConflictError)
    async def provenance_conflict_handler(
        _request: Request,
        exception: ProvenanceRecordConflictError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "provenance_record_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ProvenanceRecordNotFoundError)
    async def provenance_not_found_handler(
        _request: Request,
        exception: ProvenanceRecordNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "provenance_record_not_found",
                "detail": str(exception),
            },
        )

    @app.exception_handler(
        ResourceClassificationAlreadyExistsError
    )
    async def classification_exists_handler(
        _request: Request,
        exception: ResourceClassificationAlreadyExistsError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "code": "resource_classification_conflict",
                "detail": str(exception),
            },
        )

    @app.exception_handler(ResourceClassificationNotFoundError)
    async def classification_not_found_handler(
        _request: Request,
        exception: ResourceClassificationNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "code": "resource_classification_not_found",
                "detail": str(exception),
            },
        )
