from pathlib import Path

from fastapi.testclient import TestClient

from eke.presentation.api import APISettings, create_app


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            APISettings(
                environment="test",
                database_url=(
                    "sqlite+pysqlite:///"
                    f"{tmp_path / 'versions-api.db'}"
                ),
            )
        )
    )


def create_resource(client: TestClient) -> str:
    response = client.post(
        "/resources",
        json={
            "identifiers": [
                {
                    "scheme": "CELEX",
                    "value": "32023R1114",
                }
            ],
            "resource_type": "REGULATION",
            "status": "IN_FORCE",
        },
    )
    assert response.status_code == 201
    return str(response.json()["resource_uuid"])


def version_payload(
    previous_version_uuid: str | None = None,
) -> dict[str, object]:
    return {
        "status": "IN_FORCE",
        "valid_from": "2024-01-01",
        "valid_to": None,
        "previous_version_uuid": previous_version_uuid,
    }


def test_add_list_get_and_delete_version(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        created = client.post(
            f"/resources/{resource_uuid}/versions",
            json=version_payload(),
        )
        version_uuid = created.json()["version_uuid"]

        listed = client.get(
            f"/resources/{resource_uuid}/versions"
        )
        fetched = client.get(
            f"/resources/{resource_uuid}/versions/"
            f"{version_uuid}"
        )
        deleted = client.delete(
            f"/resources/{resource_uuid}/versions/"
            f"{version_uuid}"
        )

    assert created.status_code == 201
    assert created.headers["location"].endswith(version_uuid)
    assert listed.json() == [created.json()]
    assert fetched.json() == created.json()
    assert deleted.status_code == 204


def test_missing_previous_version_returns_conflict(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.post(
            f"/resources/{resource_uuid}/versions",
            json=version_payload(
                "00000000-0000-0000-0000-000000000001"
            ),
        )

    assert response.status_code == 409
    assert response.json()["code"] == (
        "resource_version_conflict"
    )


def test_missing_version_returns_not_found(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.get(
            f"/resources/{resource_uuid}/versions/"
            "00000000-0000-0000-0000-000000000001"
        )

    assert response.status_code == 404
    assert response.json()["code"] == (
        "resource_version_not_found"
    )
