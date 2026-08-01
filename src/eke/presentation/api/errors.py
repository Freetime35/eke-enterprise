"""HTTP exception mapping for application errors."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from eke.application.resources import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register application-to-HTTP exception mappings."""
    if not isinstance(app, FastAPI):
        raise TypeError("app must be a FastAPI")

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
