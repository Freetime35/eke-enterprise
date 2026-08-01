"""Tests for FastAPI dependency providers."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.resources import ResourceService
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_resource_service,
)


def test_resource_service_dependency_is_resolvable(
    tmp_path: Path,
) -> None:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'dependency.db'}"
            ),
        )
    )

    with TestClient(app) as client:
        request = client.get("/health").request
        assert request is not None
        service = app.state.container.resource_service()

    assert isinstance(service, ResourceService)
    assert callable(get_resource_service)
