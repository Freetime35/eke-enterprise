"""Explicit recovery of stale running import jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from eke.domain.imports import ImportJob


@dataclass(frozen=True, slots=True)
class StaleImportJobRecovery:
    """Represent one persisted stale-job recovery."""

    job: ImportJob
    recovered_at: datetime
    threshold_seconds: int

    def __post_init__(self) -> None:
        if not isinstance(self.job, ImportJob):
            raise TypeError("job must be an ImportJob")
        if not isinstance(self.recovered_at, datetime):
            raise TypeError(
                "recovered_at must be a datetime"
            )
        if (
            self.recovered_at.tzinfo is None
            or self.recovered_at.utcoffset() is None
        ):
            raise ValueError(
                "recovered_at must be timezone-aware"
            )
        if not isinstance(self.threshold_seconds, int):
            raise TypeError(
                "threshold_seconds must be an integer"
            )
        if self.threshold_seconds < 1:
            raise ValueError(
                "threshold_seconds must be greater than zero"
            )
