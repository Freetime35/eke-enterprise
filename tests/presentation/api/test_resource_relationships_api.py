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
                    f"{tmp_path / 'relationships-api.db'}"
                ),
            )
        )
    )


def create_resource(
    client: TestClient,
    value: str,
) -> str:
    response = client.post(
        "/resources",
        json={
            "identifiers": [
                {
                    "scheme": "CELEX",
                    "value": value,
                }
            ],
            "resource_type": "REGULATION",
            "status": "IN_FORCE",
        },
    )
    assert response.status_code == 201
    return str(response.json()["resource_uuid"])


def relationship_payload(
    target_uuid: str,
) -> dict[str, object]:
    return {
        "target_resource_uuid": target_uuid,
        "relationship_type": "AMENDS",
        "valid_from": "2024-01-01",
        "valid_to": None,
    }


def test_add_list_and_delete_relationship(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        source_uuid = create_resource(client, "SOURCE")
        target_uuid = create_resource(client, "TARGET")

        created = client.post(
            f"/resources/{source_uuid}/relationships",
            json=relationship_payload(target_uuid),
        )
        listed = client.get(
            f"/resources/{source_uuid}/relationships"
        )
        deleted = client.delete(
            f"/resources/{source_uuid}/relationships/"
            f"{target_uuid}",
            params={
                "relationship_type": "AMENDS",
                "valid_from": "2024-01-01",
            },
        )

    assert created.status_code == 201
    assert listed.json() == [created.json()]
    assert deleted.status_code == 204


def test_duplicate_relationship_returns_conflict(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        source_uuid = create_resource(client, "SOURCE")
        target_uuid = create_resource(client, "TARGET")
        client.post(
            f"/resources/{source_uuid}/relationships",
            json=relationship_payload(target_uuid),
        )
        response = client.post(
            f"/resources/{source_uuid}/relationships",
            json=relationship_payload(target_uuid),
        )

    assert response.status_code == 409
    assert response.json()["code"] == (
        "resource_relationship_conflict"
    )


def test_missing_target_returns_conflict(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        source_uuid = create_resource(client, "SOURCE")
        response = client.post(
            f"/resources/{source_uuid}/relationships",
            json=relationship_payload(
                "00000000-0000-0000-0000-000000000001"
            ),
        )

    assert response.status_code == 409
    assert response.json()["code"] == (
        "resource_relationship_conflict"
    )


def test_missing_relationship_returns_not_found(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        source_uuid = create_resource(client, "SOURCE")
        target_uuid = create_resource(client, "TARGET")
        response = client.delete(
            f"/resources/{source_uuid}/relationships/"
            f"{target_uuid}",
            params={
                "relationship_type": "AMENDS",
                "valid_from": "2024-01-01",
            },
        )

    assert response.status_code == 404
    assert response.json()["code"] == (
        "resource_relationship_not_found"
    )
