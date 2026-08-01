"""HTTP exception mapping for application errors."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from eke.application.resources import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
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
