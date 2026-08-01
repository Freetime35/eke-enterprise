"""Integration tests for the EUR-Lex import endpoint."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from eke.application.eurlex import (
    EurLexDocumentNotFoundError,
    EurLexImportResult,
    EurLexUpstreamError,
)
from eke.domain.identity import (
    BusinessIdentifier,
    CelexIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceType,
)
from eke.presentation.api import APISettings, create_app
from eke.presentation.api.dependencies import (
    get_eurlex_import_service,
)


class FakeImportService:
    def __init__(
        self,
        *,
        created: bool = True,
        exception: Exception | None = None,
    ) -> None:
        self.created = created
        self.exception = exception
        self.calls: list[CelexIdentifier] = []

    def import_resource(
        self,
        celex_identifier: CelexIdentifier,
    ) -> EurLexImportResult:
        self.calls.append(celex_identifier)
        if self.exception is not None:
            raise self.exception

        resource = Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(
                BusinessIdentifier(
                    IdentifierScheme.CELEX,
                    celex_identifier.value,
                ),
            ),
            resource_type=ResourceType.REGULATION,
            status=ResourceStatus.IN_FORCE,
        )
        return EurLexImportResult(
            resource=resource,
            created=self.created,
        )


def make_client(
    tmp_path: Path,
    service: FakeImportService,
) -> TestClient:
    app = create_app(
        APISettings(
            environment="test",
            database_url=(
                "sqlite+pysqlite:///"
                f"{tmp_path / 'eurlex-import-api.db'}"
            ),
        )
    )
    app.dependency_overrides[
        get_eurlex_import_service
    ] = lambda: service
    return TestClient(app)


def test_import_created_resource_returns_201(
    tmp_path: Path,
) -> None:
    service = FakeImportService(created=True)

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex",
            json={"celex": "32023R1114"},
        )

    assert response.status_code == 201
    assert response.json()["created"] is True
    assert (
        response.json()["resource"]["identifiers"][0]["value"]
        == "32023R1114"
    )
    assert response.headers["location"].startswith(
        "/resources/"
    )
    assert service.calls == [
        CelexIdentifier.parse("32023R1114")
    ]


def test_existing_import_returns_200(
    tmp_path: Path,
) -> None:
    service = FakeImportService(created=False)

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex",
            json={"celex": "32023R1114"},
        )

    assert response.status_code == 200
    assert response.json()["created"] is False


def test_invalid_celex_returns_422(
    tmp_path: Path,
) -> None:
    service = FakeImportService()

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex",
            json={"celex": "invalid"},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "celex must be a valid standard-form CELEX identifier"
    )
    assert service.calls == []


def test_missing_eurlex_document_returns_404(
    tmp_path: Path,
) -> None:
    service = FakeImportService(
        exception=EurLexDocumentNotFoundError(
            "EUR-Lex document not found: 32023R1114"
        )
    )

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex",
            json={"celex": "32023R1114"},
        )

    assert response.status_code == 404
    assert response.json()["code"] == (
        "eurlex_document_not_found"
    )


def test_eurlex_failure_returns_502(
    tmp_path: Path,
) -> None:
    service = FakeImportService(
        exception=EurLexUpstreamError(
            "EUR-Lex request failed"
        )
    )

    with make_client(tmp_path, service) as client:
        response = client.post(
            "/imports/eurlex",
            json={"celex": "32023R1114"},
        )

    assert response.status_code == 502
    assert response.json()["code"] == (
        "eurlex_upstream_error"
    )
