"""Tests for the FastAPI application bootstrap."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eke.presentation.api import APISettings, create_app


def make_settings(
    tmp_path: Path,
    *,
    docs_enabled: bool = True,
) -> APISettings:
    return APISettings(
        application_name="EKE Test",
        application_version="test",
        environment="test",
        database_url=(
            "sqlite+pysqlite:///"
            f"{tmp_path / 'api-test.db'}"
        ),
        docs_enabled=docs_enabled,
    )


def test_application_metadata(tmp_path: Path) -> None:
    app = create_app(make_settings(tmp_path))

    assert app.title == "EKE Test"
    assert app.version == "test"


def test_lifespan_initializes_and_disposes_container(
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(tmp_path))

    assert not app.state.ready

    with TestClient(app):
        assert app.state.ready
        assert app.state.container is not None

    assert not app.state.ready


def test_health_endpoint(tmp_path: Path) -> None:
    app = create_app(make_settings(tmp_path))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_endpoint(tmp_path: Path) -> None:
    app = create_app(make_settings(tmp_path))

    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_lifespan_applies_database_migrations(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "api-test.db"
    app = create_app(make_settings(tmp_path))

    with TestClient(app):
        pass

    assert database_path.exists()


def test_openapi_and_docs_are_enabled(
    tmp_path: Path,
) -> None:
    app = create_app(make_settings(tmp_path))

    with TestClient(app) as client:
        assert client.get("/openapi.json").status_code == 200
        assert client.get("/docs").status_code == 200


def test_docs_can_be_disabled(tmp_path: Path) -> None:
    app = create_app(
        make_settings(
            tmp_path,
            docs_enabled=False,
        )
    )

    with TestClient(app) as client:
        assert client.get("/openapi.json").status_code == 404
        assert client.get("/docs").status_code == 404


def test_create_app_rejects_invalid_settings() -> None:
    with pytest.raises(
        TypeError,
        match="settings must be an APISettings or None",
    ):
        create_app("invalid")  # type: ignore[arg-type]
