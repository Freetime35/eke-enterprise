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
from eke.infrastructure.eurlex import HttpxEurLexClient
from eke.presentation.api.container import build_container
from eke.presentation.api.errors import (
    register_exception_handlers,
)
from eke.presentation.api.openapi import (
    OPENAPI_TAGS,
    generate_operation_id,
)
from eke.presentation.api.routes import (
    eurlex_imports_router,
    resource_classifications_router,
    resource_provenance_router,
    resource_relationships_router,
    resource_titles_router,
    resource_versions_router,
    resources_router,
    system_router,
)
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
        raise TypeError(
            "settings must be an APISettings or None"
        )

    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncIterator[None]:
        engine = create_sqlite_engine(
            resolved_settings.database_url
        )
        eurlex_client = HttpxEurLexClient()
        upgrade_database(engine)
        app.state.container = build_container(
            engine,
            create_session_factory(engine),
            eurlex_client=eurlex_client,
        )
        app.state.ready = True
        try:
            yield
        finally:
            app.state.ready = False
            eurlex_client.close()
            engine.dispose()

    docs_url = (
        "/docs" if resolved_settings.docs_enabled else None
    )
    redoc_url = (
        "/redoc" if resolved_settings.docs_enabled else None
    )
    openapi_url = (
        "/openapi.json"
        if resolved_settings.docs_enabled
        else None
    )

    app = FastAPI(
        title=resolved_settings.application_name,
        version=resolved_settings.application_version,
        description=(
            "Enterprise API for canonical legal knowledge "
            "engineering."
        ),
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        openapi_tags=OPENAPI_TAGS,
        generate_unique_id_function=generate_operation_id,
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.ready = False

    register_exception_handlers(app)
    app.include_router(system_router)
    app.include_router(resources_router)
    app.include_router(resource_titles_router)
    app.include_router(resource_versions_router)
    app.include_router(resource_relationships_router)
    app.include_router(resource_provenance_router)
    app.include_router(resource_classifications_router)
    app.include_router(eurlex_imports_router)

    return app
