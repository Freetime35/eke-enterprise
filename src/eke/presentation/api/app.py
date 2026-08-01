"""FastAPI application factory and composition root."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from eke.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    upgrade_database,
)
from eke.presentation.api.container import build_container
from eke.presentation.api.routes import system_router
from eke.presentation.api.settings import APISettings


def create_app(
    settings: APISettings | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = (
        settings
        if settings is not None
        else APISettings.from_environment()
    )
    if not isinstance(resolved_settings, APISettings):
        raise TypeError("settings must be an APISettings or None")

    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncIterator[None]:
        engine = create_sqlite_engine(
            resolved_settings.database_url
        )
        upgrade_database(engine)
        session_factory = create_session_factory(engine)
        app.state.container = build_container(
            engine,
            session_factory,
        )
        app.state.ready = True

        try:
            yield
        finally:
            app.state.ready = False
            engine.dispose()

    docs_url = (
        "/docs"
        if resolved_settings.docs_enabled
        else None
    )
    redoc_url = (
        "/redoc"
        if resolved_settings.docs_enabled
        else None
    )
    openapi_url = (
        "/openapi.json"
        if resolved_settings.docs_enabled
        else None
    )

    app = FastAPI(
        title=resolved_settings.application_name,
        version=resolved_settings.application_version,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.ready = False
    app.include_router(system_router)

    return app
