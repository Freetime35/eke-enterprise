"""Failed-item projection for persistent import-job results."""

from __future__ import annotations

from dataclasses import dataclass

from eke.application.eurlex.bulk_import import (
    EurLexBulkImportStatus,
)
from eke.application.eurlex.import_job_results import (
    ImportJobResultError,
    parse_import_job_results,
)


class FailedImportJobResultError(ValueError):
    """Raised when failed import-job results are unusable."""


@dataclass(frozen=True, slots=True)
class FailedImportItem:
    """Represent one failed item from a persisted bulk result."""

    celex: str
    error_code: str | None
    detail: str | None


def extract_failed_items(
    result_json: str | None,
) -> tuple[FailedImportItem, ...]:
    """Return structured FAILED items from persisted results."""
    try:
        items = parse_import_job_results(result_json)
    except ImportJobResultError as exc:
        raise FailedImportJobResultError(
            str(exc)
        ) from exc

    failed = tuple(
        FailedImportItem(
            celex=item.celex,
            error_code=item.error_code,
            detail=item.detail,
        )
        for item in items
        if item.status is EurLexBulkImportStatus.FAILED
    )

    if not failed:
        raise FailedImportJobResultError(
            "import job has no failed items"
        )

    return failed


def extract_failed_celex(
    result_json: str | None,
) -> tuple[str, ...]:
    """Return unique CELEX values for backward compatibility."""
    return tuple(
        item.celex
        for item in extract_failed_items(result_json)
    )
