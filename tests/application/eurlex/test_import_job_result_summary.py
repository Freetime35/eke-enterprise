"""Tests for import-job result summaries."""

from eke.application.eurlex import (
    EurLexBulkImportStatus,
)
from eke.application.eurlex.import_job_result_summary import (
    ImportJobResultSummary,
)
from eke.application.eurlex.import_job_results import (
    ImportJobResultItem,
)


def make_item(
    status: EurLexBulkImportStatus,
) -> ImportJobResultItem:
    return ImportJobResultItem(
        celex="32023R1114",
        status=status,
        resource_uuid=None,
        error_code=None,
        detail=None,
    )


def test_summary_counts_all_statuses() -> None:
    summary = ImportJobResultSummary.from_items(
        (
            make_item(
                EurLexBulkImportStatus.CREATED
            ),
            make_item(
                EurLexBulkImportStatus.CREATED
            ),
            make_item(
                EurLexBulkImportStatus.EXISTING
            ),
            make_item(
                EurLexBulkImportStatus.FAILED
            ),
        )
    )

    assert summary.total == 4
    assert summary.counts == {
        EurLexBulkImportStatus.CREATED: 2,
        EurLexBulkImportStatus.EXISTING: 1,
        EurLexBulkImportStatus.FAILED: 1,
    }
    assert summary.success_count == 3
    assert summary.failure_count == 1
    assert summary.success_rate == 0.75
    assert summary.failure_rate == 0.25


def test_empty_summary_has_zero_rates() -> None:
    summary = ImportJobResultSummary.from_items(())

    assert summary.total == 0
    assert summary.success_count == 0
    assert summary.failure_count == 0
    assert summary.success_rate == 0.0
    assert summary.failure_rate == 0.0
