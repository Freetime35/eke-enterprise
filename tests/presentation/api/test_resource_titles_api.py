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
                    f"{tmp_path / 'titles-api.db'}"
                ),
            )
        )
    )


def create_resource(client: TestClient) -> str:
    response = client.post(
        "/resources",
        json={
            "identifiers": [{"scheme": "CELEX", "value": "32023R1114"}],
            "resource_type": "REGULATION",
            "status": "IN_FORCE",
        },
    )
    assert response.status_code == 201
    return str(response.json()["resource_uuid"])


def payload() -> dict[str, object]:
    return {
        "language": "fr",
        "value": "Titre français",
        "valid_from": "2024-01-01",
        "valid_to": None,
    }


def test_add_list_and_delete_title(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        created = client.post(
            f"/resources/{resource_uuid}/titles",
            json=payload(),
        )
        listed = client.get(f"/resources/{resource_uuid}/titles")
        deleted = client.delete(
            f"/resources/{resource_uuid}/titles/fr",
            params={"valid_from": "2024-01-01"},
        )

    assert created.status_code == 201
    assert created.json() == payload()
    assert listed.json() == [payload()]
    assert deleted.status_code == 204


def test_duplicate_title_returns_conflict(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        client.post(f"/resources/{resource_uuid}/titles", json=payload())
        response = client.post(
            f"/resources/{resource_uuid}/titles",
            json=payload(),
        )

    assert response.status_code == 409
    assert response.json()["code"] == "resource_title_conflict"


def test_delete_missing_title_returns_not_found(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.delete(
            f"/resources/{resource_uuid}/titles/fr",
            params={"valid_from": "2024-01-01"},
        )

    assert response.status_code == 404
    assert response.json()["code"] == "resource_title_not_found"
