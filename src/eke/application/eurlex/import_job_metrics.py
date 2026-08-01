"""Operational metrics for persistent import jobs."""

from __future__ import annotations

from dataclasses import dataclass

from eke.application.eurlex.import_job_summary import (
    ImportJobStatusSummary,
)
from eke.domain.imports import ImportJobStatus


@dataclass(frozen=True, slots=True)
class ImportJobOperationalMetrics:
    """Represent derived operational import-job indicators."""

    total: int
    active: int
    terminal: int
    successful: int
    unsuccessful: int
    cancelled: int
    completion_rate: float
    failure_rate: float

    def __post_init__(self) -> None:
        integer_values = (
            self.total,
            self.active,
            self.terminal,
            self.successful,
            self.unsuccessful,
            self.cancelled,
        )
        if any(
            not isinstance(value, int)
            for value in integer_values
        ):
            raise TypeError(
                "metric counters must be integers"
            )
        if any(value < 0 for value in integer_values):
            raise ValueError(
                "metric counters must not be negative"
            )
        if self.active + self.terminal != self.total:
            raise ValueError(
                "active and terminal must equal total"
            )
        if (
            self.successful
            + self.unsuccessful
            + self.cancelled
            != self.terminal
        ):
            raise ValueError(
                "terminal outcome counters must equal terminal"
            )

        for name, value in (
            ("completion_rate", self.completion_rate),
            ("failure_rate", self.failure_rate),
        ):
            if not isinstance(value, float):
                raise TypeError(f"{name} must be a float")
            if not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be between 0 and 1"
                )

    @classmethod
    def from_summary(
        cls,
        summary: ImportJobStatusSummary,
    ) -> ImportJobOperationalMetrics:
        """Derive metrics from one complete status summary."""
        if not isinstance(summary, ImportJobStatusSummary):
            raise TypeError(
                "summary must be an ImportJobStatusSummary"
            )

        active = (
            summary.count(ImportJobStatus.PENDING)
            + summary.count(ImportJobStatus.RUNNING)
        )
        successful = summary.count(
            ImportJobStatus.COMPLETED
        )
        unsuccessful = (
            summary.count(ImportJobStatus.FAILED)
            + summary.count(
                ImportJobStatus.PARTIALLY_FAILED
            )
        )
        cancelled = summary.count(
            ImportJobStatus.CANCELLED
        )
        terminal = successful + unsuccessful + cancelled

        completion_rate = (
            successful / terminal
            if terminal
            else 0.0
        )
        failure_rate = (
            unsuccessful / terminal
            if terminal
            else 0.0
        )

        return cls(
            total=summary.total,
            active=active,
            terminal=terminal,
            successful=successful,
            unsuccessful=unsuccessful,
            cancelled=cancelled,
            completion_rate=completion_rate,
            failure_rate=failure_rate,
        )
