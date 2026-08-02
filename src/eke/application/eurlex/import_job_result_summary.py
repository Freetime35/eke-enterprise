"""Aggregate statistics for import-job result items."""

from __future__ import annotations

from dataclasses import dataclass

from eke.application.eurlex.bulk_import import (
    EurLexBulkImportStatus,
)
from eke.application.eurlex.import_job_results import (
    ImportJobResultItem,
)


@dataclass(frozen=True, slots=True)
class ImportJobResultSummary:
    """Represent aggregate item-level import outcomes."""

    total: int
    counts: dict[EurLexBulkImportStatus, int]
    success_count: int
    failure_count: int
    success_rate: float
    failure_rate: float

    def __post_init__(self) -> None:
        if not isinstance(self.total, int):
            raise TypeError("total must be an integer")
        if self.total < 0:
            raise ValueError("total must not be negative")
        if set(self.counts) != set(
            EurLexBulkImportStatus
        ):
            raise ValueError(
                "counts must cover every item status"
            )
        if any(
            not isinstance(value, int) or value < 0
            for value in self.counts.values()
        ):
            raise ValueError(
                "counts must contain non-negative integers"
            )
        if sum(self.counts.values()) != self.total:
            raise ValueError(
                "counts must add up to total"
            )
        if (
            self.success_count
            + self.failure_count
            != self.total
        ):
            raise ValueError(
                "success and failure counts "
                "must add up to total"
            )
        for name, value in (
            ("success_rate", self.success_rate),
            ("failure_rate", self.failure_rate),
        ):
            if not isinstance(value, float):
                raise TypeError(
                    f"{name} must be a float"
                )
            if value < 0.0 or value > 1.0:
                raise ValueError(
                    f"{name} must be between zero and one"
                )

    @classmethod
    def from_items(
        cls,
        items: tuple[ImportJobResultItem, ...],
    ) -> ImportJobResultSummary:
        """Build a summary from parsed result items."""
        if not isinstance(items, tuple):
            raise TypeError("items must be a tuple")
        if any(
            not isinstance(item, ImportJobResultItem)
            for item in items
        ):
            raise TypeError(
                "items must contain ImportJobResultItem values"
            )

        counts = {
            status: sum(
                item.status is status
                for item in items
            )
            for status in EurLexBulkImportStatus
        }
        total = len(items)
        failure_count = counts[
            EurLexBulkImportStatus.FAILED
        ]
        success_count = total - failure_count

        if total == 0:
            success_rate = 0.0
            failure_rate = 0.0
        else:
            success_rate = success_count / total
            failure_rate = failure_count / total

        return cls(
            total=total,
            counts=counts,
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            failure_rate=failure_rate,
        )
