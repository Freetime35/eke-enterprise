"""Failed-item extraction for persistent import-job results."""

from __future__ import annotations

from json import JSONDecodeError, loads
from typing import Any


class FailedImportJobResultError(ValueError):
    """Raised when persisted import-job results are unusable."""


def extract_failed_celex(
    result_json: str | None,
) -> tuple[str, ...]:
    """Return unique CELEX identifiers whose item status is FAILED."""
    if result_json is None:
        raise FailedImportJobResultError(
            "import job has no persisted item results"
        )
    if not isinstance(result_json, str):
        raise TypeError(
            "result_json must be a string or None"
        )

    try:
        payload: Any = loads(result_json)
    except JSONDecodeError as exc:
        raise FailedImportJobResultError(
            "import job result payload is invalid JSON"
        ) from exc

    if not isinstance(payload, list):
        raise FailedImportJobResultError(
            "import job result payload must be a list"
        )

    failed: list[str] = []

    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise FailedImportJobResultError(
                f"import job result item {index} "
                "must be an object"
            )

        status = item.get("status")
        celex = item.get("celex")

        if status != "FAILED":
            continue

        if (
            not isinstance(celex, str)
            or not celex.strip()
        ):
            raise FailedImportJobResultError(
                f"failed result item {index} "
                "must define celex"
            )

        normalized = celex.strip().upper()

        if normalized not in failed:
            failed.append(normalized)

    if not failed:
        raise FailedImportJobResultError(
            "import job has no failed items to retry"
        )

    return tuple(failed)
