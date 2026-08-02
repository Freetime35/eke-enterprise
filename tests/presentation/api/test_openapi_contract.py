"""OpenAPI contract tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from eke.presentation.api import APISettings, create_app

EXPECTED_TAGS = {
    "system",
    "resources",
    "resource-titles",
    "resource-versions",
    "resource-relationships",
    "resource-provenance",
    "resource-classifications",
    "eurlex-imports",
    "eurlex-import-jobs",
}

EXPECTED_PATHS = {
    "/health",
    "/ready",
    "/resources",
    "/resources/by-identifier",
    "/resources/{resource_uuid}",
    "/resources/{resource_uuid}/titles",
    "/resources/{resource_uuid}/titles/{language}",
    "/resources/{resource_uuid}/versions",
    "/resources/{resource_uuid}/versions/{version_uuid}",
    "/resources/{resource_uuid}/relationships",
    (
        "/resources/{resource_uuid}/relationships/"
        "{target_resource_uuid}"
    ),
    "/resources/{resource_uuid}/provenance",
    "/resources/{resource_uuid}/classifications",
    (
        "/resources/{resource_uuid}/classifications/"
        "{scheme}/{code}/{language}"
    ),
    "/imports/eurlex",
    "/imports/eurlex/bulk",
    "/imports/eurlex/jobs",
    "/imports/eurlex/jobs/{job_uuid}",
    "/imports/eurlex/jobs/{job_uuid}/run",
    "/imports/eurlex/jobs/{job_uuid}/submit",
    "/imports/eurlex/jobs/{job_uuid}/cancel",
    "/imports/eurlex/jobs/{job_uuid}/retry",
    "/imports/eurlex/jobs/{job_uuid}/lineage",
    "/imports/eurlex/jobs/summary",
    "/imports/eurlex/jobs/metrics",
    "/imports/eurlex/jobs/durations",
    "/imports/eurlex/jobs/stale",
}


def make_client(tmp_path: Path) -> TestClient:
    return TestClient(
        create_app(
            APISettings(
                application_name="EKE Contract Test",
                application_version="contract",
                environment="test",
                database_url=(
                    "sqlite+pysqlite:///"
                    f"{tmp_path / 'openapi-contract.db'}"
                ),
            )
        )
    )


def load_schema(tmp_path: Path) -> dict[str, Any]:
    with make_client(tmp_path) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    schema: dict[str, Any] = response.json()
    return schema


def test_openapi_metadata_is_stable(tmp_path: Path) -> None:
    schema = load_schema(tmp_path)

    assert schema["info"]["title"] == "EKE Contract Test"
    assert schema["info"]["version"] == "contract"
    assert schema["info"]["description"] == (
        "Enterprise API for canonical legal knowledge "
        "engineering."
    )


def test_openapi_declares_all_public_tags(
    tmp_path: Path,
) -> None:
    schema = load_schema(tmp_path)

    tags = {
        tag["name"]
        for tag in schema["tags"]
    }

    assert tags == EXPECTED_TAGS


def test_openapi_declares_all_public_paths(
    tmp_path: Path,
) -> None:
    schema = load_schema(tmp_path)

    assert set(schema["paths"]) == EXPECTED_PATHS


def test_operation_ids_are_unique_and_stable(
    tmp_path: Path,
) -> None:
    schema = load_schema(tmp_path)
    operation_ids: list[str] = []

    for path_item in schema["paths"].values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            if operation_id is not None:
                operation_ids.append(operation_id)

    assert len(operation_ids) == len(set(operation_ids))

    assert "resources_create_resource" in operation_ids
    assert "resources_search_resources" in operation_ids

    assert (
        "resource_titles_add_resource_title"
        in operation_ids
    )
    assert (
        "resource_versions_add_resource_version"
        in operation_ids
    )
    assert (
        "resource_relationships_add_resource_relationship"
        in operation_ids
    )
    assert (
        "resource_provenance_add_resource_provenance"
        in operation_ids
    )
    assert (
        "resource_classifications_add_resource_classification"
        in operation_ids
    )

    assert (
        "eurlex_imports_import_eurlex_resource"
        in operation_ids
    )
    assert (
        "eurlex_imports_bulk_import_eurlex_resources"
        in operation_ids
    )

    assert (
        "eurlex_import_jobs_create_import_job"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_get_import_job"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_run_import_job"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_submit_import_job"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_search_import_jobs"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_cancel_import_job"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_retry_import_job"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_get_import_job_lineage"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_summarize_import_jobs"
        in operation_ids
    )
    assert (
        "eurlex_import_jobs_get_import_job_metrics"
        in operation_ids
    )
    assert (
    "eurlex_import_jobs_get_import_job_duration_statistics"
    in operation_ids
    )
    assert (
    "eurlex_import_jobs_get_stale_import_jobs"
    in operation_ids
    )

def test_openapi_contains_validation_error_schema(
    tmp_path: Path,
) -> None:
    schema = load_schema(tmp_path)

    component_schemas = schema["components"]["schemas"]

    assert "HTTPValidationError" in component_schemas
    assert "ValidationError" in component_schemas