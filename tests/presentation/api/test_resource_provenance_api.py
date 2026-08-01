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
                    f"{tmp_path / 'provenance-api.db'}"
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


def provenance_payload() -> dict[str, object]:
    return {
        "source": "EUR_LEX",
        "source_reference": "32023R1114",
        "acquired_at": "2026-08-01T12:00:00Z",
        "acquisition_method": "API",
        "checksum": "sha256:abc",
    }


def test_add_list_and_delete_provenance(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)

        created = client.post(
            f"/resources/{resource_uuid}/provenance",
            json=provenance_payload(),
        )
        listed = client.get(
            f"/resources/{resource_uuid}/provenance"
        )
        deleted = client.delete(
            f"/resources/{resource_uuid}/provenance",
            params=provenance_payload(),
        )

    assert created.status_code == 201
    assert listed.json() == [created.json()]
    assert deleted.status_code == 204


def test_duplicate_provenance_returns_conflict(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        client.post(
            f"/resources/{resource_uuid}/provenance",
            json=provenance_payload(),
        )
        response = client.post(
            f"/resources/{resource_uuid}/provenance",
            json=provenance_payload(),
        )

    assert response.status_code == 409
    assert response.json()["code"] == (
        "provenance_record_conflict"
    )


def test_missing_provenance_returns_not_found(
    tmp_path: Path,
) -> None:
    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.delete(
            f"/resources/{resource_uuid}/provenance",
            params=provenance_payload(),
        )

    assert response.status_code == 404
    assert response.json()["code"] == (
        "provenance_record_not_found"
    )


def test_naive_acquired_at_is_rejected(
    tmp_path: Path,
) -> None:
    payload = provenance_payload()
    payload["acquired_at"] = "2026-08-01T12:00:00"

    with make_client(tmp_path) as client:
        resource_uuid = create_resource(client)
        response = client.post(
            f"/resources/{resource_uuid}/provenance",
            json=payload,
        )

    assert response.status_code == 422
