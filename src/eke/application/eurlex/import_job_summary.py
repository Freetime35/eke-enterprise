"""Import-job status summary value."""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.imports import ImportJobStatus


@dataclass(frozen=True, slots=True)
class ImportJobStatusSummary:
    """Represent aggregate import-job counts by lifecycle state."""

    total: int
    counts: dict[ImportJobStatus, int]

    def __post_init__(self) -> None:
        if not isinstance(self.total, int):
            raise TypeError("total must be an integer")
        if self.total < 0:
            raise ValueError("total must not be negative")
        if not isinstance(self.counts, dict):
            raise TypeError("counts must be a dictionary")
        if set(self.counts) != set(ImportJobStatus):
            raise ValueError(
                "counts must contain every ImportJobStatus"
            )
        if any(
            not isinstance(status, ImportJobStatus)
            for status in self.counts
        ):
            raise TypeError(
                "counts keys must be ImportJobStatus values"
            )
        if any(
            not isinstance(value, int)
            for value in self.counts.values()
        ):
            raise TypeError(
                "counts values must be integers"
            )
        if any(value < 0 for value in self.counts.values()):
            raise ValueError(
                "counts values must not be negative"
            )
        if sum(self.counts.values()) != self.total:
            raise ValueError(
                "total must equal the sum of status counts"
            )

    def count(
        self,
        status: ImportJobStatus,
    ) -> int:
        """Return the count for one lifecycle state."""
        if not isinstance(status, ImportJobStatus):
            raise TypeError(
                "status must be an ImportJobStatus"
            )
        return self.counts[status]
