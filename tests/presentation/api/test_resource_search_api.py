"""Integration tests for Resource search and pagination."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from eke.presentation.api import APISettings, create_app


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            APISettings(
                application_name="EKE Test",
                application_version="test",
                environment="test",
                database_url=(
                    "sqlite+pysqlite:///"
                    f"{tmp_path / 'search-api.db'}"
                ),
            )
        )
    )


def create_resource(
    client: TestClient,
    *,
    value: str,
    scheme: str = "CELEX",
    resource_type: str = "REGULATION",
    status: str = "IN_FORCE",
) -> dict[str, object]:
    response = client.post(
        "/resources",
        json={
            "identifiers": [
                {
                    "scheme": scheme,
                    "value": value,
                }
            ],
            "resource_type": resource_type,
            "status": status,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_search_returns_paginated_results(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        create_resource(client, value="A")
        create_resource(client, value="B")
        create_resource(
            client,
            value="C",
            scheme="ELI",
            resource_type="DIRECTIVE",
            status="REPEALED",
        )

        response = client.get(
            "/resources",
            params={
                "identifier_scheme": "CELEX",
                "resource_type": "REGULATION",
                "status": "IN_FORCE",
                "limit": 1,
                "offset": 1,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert len(body["items"]) == 1


def test_search_without_matches_returns_empty_page(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        response = client.get(
            "/resources",
            params={"status": "REPEALED"},
        )

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "limit": 20,
        "offset": 0,
    }


def test_search_rejects_invalid_pagination(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        invalid_limit = client.get(
            "/resources",
            params={"limit": 0},
        )
        invalid_offset = client.get(
            "/resources",
            params={"offset": -1},
        )

    assert invalid_limit.status_code == 422
    assert invalid_offset.status_code == 422
