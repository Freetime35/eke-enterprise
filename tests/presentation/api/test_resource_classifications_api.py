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
                    f"{tmp_path / 'classifications-api.db'}"
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


def classification_payload() -> dict[str, object]:
    return {
        "scheme": "EUROVOC",
        "code": "1001",
        "language": "fr",
        "label": "Marchés financiers",
        "valid_from": "2024-01-01",
        "valid_to": None,
    }


def test_add_list_and_delete_classification(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)

        created = client.post(
            f"/resources/{resource_uuid}/classifications",
            json=classification_payload(),
        )
        listed = client.get(
            f"/resources/{resource_uuid}/classifications"
        )
        deleted = client.delete(
            f"/resources/{resource_uuid}/classifications/"
            "EUROVOC/1001/fr"
        )

    assert created.status_code == 201
    assert created.json() == classification_payload()
    assert listed.json() == [classification_payload()]
    assert deleted.status_code == 204


def test_duplicate_classification_returns_conflict(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        client.post(
            f"/resources/{resource_uuid}/classifications",
            json=classification_payload(),
        )
        response = client.post(
            f"/resources/{resource_uuid}/classifications",
            json=classification_payload(),
        )

    assert response.status_code == 409
    assert response.json()["code"] == (
        "resource_classification_conflict"
    )


def test_missing_classification_returns_not_found(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.delete(
            f"/resources/{resource_uuid}/classifications/"
            "EUROVOC/1001/fr"
        )

    assert response.status_code == 404
    assert response.json()["code"] == (
        "resource_classification_not_found"
    )


def test_invalid_classification_is_rejected(
    tmp_path: Path,
) -> None:
    payload = classification_payload()
    payload["scheme"] = "INVALID"

    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.post(
            f"/resources/{resource_uuid}/classifications",
            json=payload,
        )

    assert response.status_code == 422
