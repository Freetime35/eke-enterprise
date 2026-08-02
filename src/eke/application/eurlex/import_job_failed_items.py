"""Failed-item extraction for persistent import-job results."""

from __future__ import annotations

from dataclasses import dataclass
from json import JSONDecodeError, loads
from typing import Any


class FailedImportJobResultError(ValueError):
    """Raised when persisted import-job results are unusable."""


@dataclass(frozen=True, slots=True)
class FailedImportItem:
    """Represent one failed item from a persisted bulk result."""

    celex: str
    error_code: str | None
    detail: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.celex, str):
            raise TypeError("celex must be a string")
        if not self.celex.strip():
            raise ValueError("celex must not be empty")
        if (
            self.error_code is not None
            and not isinstance(self.error_code, str)
        ):
            raise TypeError(
                "error_code must be a string or None"
            )
        if (
            self.detail is not None
            and not isinstance(self.detail, str)
        ):
            raise TypeError(
                "detail must be a string or None"
            )


def extract_failed_items(
    result_json: str | None,
) -> tuple[FailedImportItem, ...]:
    """Return structured FAILED items from persisted results."""
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

    failed: list[FailedImportItem] = []
    seen: set[str] = set()

    for index, value in enumerate(payload):
        if not isinstance(value, dict):
            raise FailedImportJobResultError(
                f"import job result item {index} "
                "must be an object"
            )

        if value.get("status") != "FAILED":
            continue

        celex = value.get("celex")
        error_code = value.get("error_code")
        detail = value.get("detail")

        if (
            not isinstance(celex, str)
            or not celex.strip()
        ):
            raise FailedImportJobResultError(
                f"failed result item {index} "
                "must define celex"
            )
        if (
            error_code is not None
            and not isinstance(error_code, str)
        ):
            raise FailedImportJobResultError(
                f"failed result item {index} "
                "has invalid error_code"
            )
        if (
            detail is not None
            and not isinstance(detail, str)
        ):
            raise FailedImportJobResultError(
                f"failed result item {index} "
                "has invalid detail"
            )

        normalized = celex.strip().upper()

        if normalized in seen:
            continue

        seen.add(normalized)
        failed.append(
            FailedImportItem(
                celex=normalized,
                error_code=error_code,
                detail=detail,
            )
        )

    if not failed:
        raise FailedImportJobResultError(
            "import job has no failed items"
        )

    return tuple(failed)


def extract_failed_celex(
    result_json: str | None,
) -> tuple[str, ...]:
    """Return unique CELEX values for backward compatibility."""
    return tuple(
        item.celex
        for item in extract_failed_items(result_json)
    )
