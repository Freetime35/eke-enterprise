"""Tests for import-job operational metrics."""

from eke.application.eurlex import (
    ImportJobOperationalMetrics,
    ImportJobStatusSummary,
)
from eke.domain.imports import ImportJobStatus


def make_summary(
    *,
    pending: int = 0,
    running: int = 0,
    completed: int = 0,
    partially_failed: int = 0,
    failed: int = 0,
    cancelled: int = 0,
) -> ImportJobStatusSummary:
    counts = {
        status: 0
        for status in ImportJobStatus
    }
    counts[ImportJobStatus.PENDING] = pending
    counts[ImportJobStatus.RUNNING] = running
    counts[ImportJobStatus.COMPLETED] = completed
    counts[
        ImportJobStatus.PARTIALLY_FAILED
    ] = partially_failed
    counts[ImportJobStatus.FAILED] = failed
    counts[ImportJobStatus.CANCELLED] = cancelled

    return ImportJobStatusSummary(
        total=sum(counts.values()),
        counts=counts,
    )


def test_metrics_are_derived_from_summary() -> None:
    metrics = ImportJobOperationalMetrics.from_summary(
        make_summary(
            pending=2,
            running=1,
            completed=6,
            partially_failed=1,
            failed=2,
            cancelled=1,
        )
    )

    assert metrics.total == 13
    assert metrics.active == 3
    assert metrics.terminal == 10
    assert metrics.successful == 6
    assert metrics.unsuccessful == 3
    assert metrics.cancelled == 1
    assert metrics.completion_rate == 0.6
    assert metrics.failure_rate == 0.3


def test_empty_summary_has_zero_rates() -> None:
    metrics = ImportJobOperationalMetrics.from_summary(
        make_summary()
    )

    assert metrics.total == 0
    assert metrics.completion_rate == 0.0
    assert metrics.failure_rate == 0.0
