"""Import-job search criteria and paginated result."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from eke.domain.imports import ImportJob, ImportJobStatus


@dataclass(frozen=True, slots=True)
class ImportJobSearchCriteria:
    """Define stable filters and offset pagination for import jobs."""

    status: ImportJobStatus | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    limit: int = 20
    offset: int = 0

    def __post_init__(self) -> None:
        if (
            self.status is not None
            and not isinstance(self.status, ImportJobStatus)
        ):
            raise TypeError(
                "status must be an ImportJobStatus or None"
            )

        self._validate_datetime(
            self.created_from,
            "created_from",
        )
        self._validate_datetime(
            self.created_to,
            "created_to",
        )

        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_from > self.created_to
        ):
            raise ValueError(
                "created_from must not be after created_to"
            )

        if not isinstance(self.limit, int):
            raise TypeError("limit must be an integer")
        if not 1 <= self.limit <= 100:
            raise ValueError(
                "limit must be between 1 and 100"
            )

        if not isinstance(self.offset, int):
            raise TypeError("offset must be an integer")
        if self.offset < 0:
            raise ValueError(
                "offset must be greater than or equal to zero"
            )

    @staticmethod
    def _validate_datetime(
        value: datetime | None,
        name: str,
    ) -> None:
        if value is None:
            return
        if not isinstance(value, datetime):
            raise TypeError(
                f"{name} must be a datetime or None"
            )
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{name} must be timezone-aware"
            )


@dataclass(frozen=True, slots=True)
class ImportJobSearchPage:
    """Represent one stable page of import jobs."""

    items: tuple[ImportJob, ...]
    total: int
    limit: int
    offset: int

    def __post_init__(self) -> None:
        if any(
            not isinstance(item, ImportJob)
            for item in self.items
        ):
            raise TypeError(
                "items must contain only ImportJob values"
            )
        if not isinstance(self.total, int):
            raise TypeError("total must be an integer")
        if self.total < 0:
            raise ValueError("total must not be negative")
        if self.total < len(self.items):
            raise ValueError(
                "total must not be smaller than item count"
            )
        if not isinstance(self.limit, int):
            raise TypeError("limit must be an integer")
        if self.limit < 1:
            raise ValueError(
                "limit must be greater than zero"
            )
        if not isinstance(self.offset, int):
            raise TypeError("offset must be an integer")
        if self.offset < 0:
            raise ValueError(
                "offset must be greater than or equal to zero"
            )
