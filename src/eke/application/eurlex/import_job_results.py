"""Structured import-job result item parsing."""

from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError, loads
from typing import Any

from eke.application.eurlex.bulk_import import (
    EurLexBulkImportStatus,
)


class ImportJobResultError(ValueError):
    """Raised when persisted import-job results are unusable."""


@dataclass(frozen=True, slots=True)
class ImportJobResultItem:
    """Represent one persisted bulk import result item."""

    celex: str
    status: EurLexBulkImportStatus
    resource_uuid: str | None
    error_code: str | None
    detail: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.celex, str):
            raise TypeError("celex must be a string")
        if not self.celex.strip():
            raise ValueError("celex must not be empty")
        if not isinstance(
            self.status,
            EurLexBulkImportStatus,
        ):
            raise TypeError(
                "status must be an EurLexBulkImportStatus"
            )
        for name, value in (
            ("resource_uuid", self.resource_uuid),
            ("error_code", self.error_code),
            ("detail", self.detail),
        ):
            if (
                value is not None
                and not isinstance(value, str)
            ):
                raise TypeError(
                    f"{name} must be a string or None"
                )


def parse_import_job_results(
    result_json: str | None,
) -> tuple[ImportJobResultItem, ...]:
    """Parse all persisted item-level import results."""
    if result_json is None:
        raise ImportJobResultError(
            "import job has no persisted item results"
        )
    if not isinstance(result_json, str):
        raise TypeError(
            "result_json must be a string or None"
        )

    try:
        payload: Any = loads(result_json)
    except JSONDecodeError as exc:
        raise ImportJobResultError(
            "import job result payload is invalid JSON"
        ) from exc

    if not isinstance(payload, list):
        raise ImportJobResultError(
            "import job result payload must be a list"
        )

    items: list[ImportJobResultItem] = []

    for index, value in enumerate(payload):
        if not isinstance(value, dict):
            raise ImportJobResultError(
                f"import job result item {index} "
                "must be an object"
            )

        celex = value.get("celex")
        status_value = value.get("status")
        resource_uuid = value.get("resource_uuid")
        error_code = value.get("error_code")
        detail = value.get("detail")

        if (
            not isinstance(celex, str)
            or not celex.strip()
        ):
            raise ImportJobResultError(
                f"import job result item {index} "
                "must define celex"
            )
        if not isinstance(status_value, str):
            raise ImportJobResultError(
                f"import job result item {index} "
                "must define status"
            )

        try:
            item_status = EurLexBulkImportStatus(
                status_value
            )
        except ValueError as exc:
            raise ImportJobResultError(
                f"import job result item {index} "
                f"has invalid status: {status_value}"
            ) from exc

        for name, field_value in (
            ("resource_uuid", resource_uuid),
            ("error_code", error_code),
            ("detail", detail),
        ):
            if (
                field_value is not None
                and not isinstance(field_value, str)
            ):
                raise ImportJobResultError(
                    f"import job result item {index} "
                    f"has invalid {name}"
                )

        items.append(
            ImportJobResultItem(
                celex=celex.strip().upper(),
                status=item_status,
                resource_uuid=resource_uuid,
                error_code=error_code,
                detail=detail,
            )
        )

    return tuple(items)
