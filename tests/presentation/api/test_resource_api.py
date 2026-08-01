"""Integration tests for Resource CRUD endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from eke.presentation.api import APISettings, create_app


def make_client(tmp_path: Path) -> TestClient:
    app = create_app(
        APISettings(
            application_name="EKE Test",
            application_version="test",
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'resource-api.db'}"
            ),
        )
    )
    return TestClient(app)


def create_payload(
    value: str = "32023R1114",
) -> dict[str, object]:
    return {
        "identifiers": [
            {
                "scheme": "CELEX",
                "value": value,
            }
        ],
        "resource_type": "REGULATION",
        "status": "PUBLISHED",
    }


def test_create_and_get_resource(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        created = client.post(
            "/resources",
            json=create_payload(),
        )

        assert created.status_code == 201
        resource_uuid = created.json()["resource_uuid"]
        assert created.headers["location"] == (
            f"/resources/{resource_uuid}"
        )

        fetched = client.get(
            f"/resources/{resource_uuid}"
        )

    assert fetched.status_code == 200
    assert fetched.json() == created.json()


def test_get_by_identifier(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        created = client.post(
            "/resources",
            json=create_payload(),
        )
        response = client.get(
            "/resources/by-identifier",
            params={
                "scheme": "CELEX",
                "value": "32023R1114",
            },
        )

    assert response.status_code == 200
    assert response.json() == created.json()


def test_update_resource(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        created = client.post(
            "/resources",
            json=create_payload(),
        )
        resource_uuid = created.json()["resource_uuid"]

        updated = client.put(
            f"/resources/{resource_uuid}",
            json={
                "identifiers": [
                    {
                        "scheme": "CELEX",
                        "value": "32013R0575",
                    }
                ],
                "resource_type": "REGULATION",
                "status": "IN_FORCE",
            },
        )

    assert updated.status_code == 200
    assert updated.json()["status"] == "IN_FORCE"
    assert updated.json()["identifiers"][0]["value"] == (
        "32013R0575"
    )


def test_delete_resource(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        created = client.post(
            "/resources",
            json=create_payload(),
        )
        resource_uuid = created.json()["resource_uuid"]

        deleted = client.delete(
            f"/resources/{resource_uuid}"
        )
        missing = client.get(
            f"/resources/{resource_uuid}"
        )

    assert deleted.status_code == 204
    assert deleted.content == b""
    assert missing.status_code == 404
    assert missing.json()["code"] == "resource_not_found"


def test_duplicate_identifier_returns_conflict(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        first = client.post(
            "/resources",
            json=create_payload(),
        )
        duplicate = client.post(
            "/resources",
            json=create_payload(),
        )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "resource_conflict"


def test_missing_resource_returns_not_found(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        response = client.get(
            "/resources/"
            "00000000-0000-0000-0000-000000000001"
        )

    assert response.status_code == 404
    assert response.json()["code"] == "resource_not_found"


def test_invalid_request_returns_validation_error(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        response = client.post(
            "/resources",
            json={
                "identifiers": [],
                "resource_type": "INVALID",
            },
        )

    assert response.status_code == 422


def test_invalid_uuid_returns_validation_failure(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        response = client.get(
            "/resources/not-a-uuid"
        )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "resource_uuid must be a valid UUID"
    )