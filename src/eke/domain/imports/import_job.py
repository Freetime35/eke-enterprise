"""Persistent EUR-Lex import job domain model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class ImportJobStatus(StrEnum):
    """Lifecycle state of an import job."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIALLY_FAILED = "PARTIALLY_FAILED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class ImportJob:
    """Represent one persistent bulk EUR-Lex import job."""

    job_uuid: UUID
    celex: tuple[str, ...]
    status: ImportJobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    retried_from_job_uuid: UUID | None = None
    total: int = 0
    created: int = 0
    existing: int = 0
    failed: int = 0
    result_json: str | None = None
    error_detail: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.job_uuid, UUID):
            raise TypeError("job_uuid must be a UUID")
        if not isinstance(self.celex, tuple):
            raise TypeError("celex must be a tuple")
        if not self.celex:
            raise ValueError("celex must not be empty")
        if any(
            not isinstance(value, str) or not value.strip()
            for value in self.celex
        ):
            raise ValueError(
                "celex must contain non-empty strings"
            )
        if len(set(self.celex)) != len(self.celex):
            raise ValueError("celex must not contain duplicates")
        if not isinstance(self.status, ImportJobStatus):
            raise TypeError(
                "status must be an ImportJobStatus"
            )
        if (
            self.retried_from_job_uuid is not None
            and not isinstance(
                self.retried_from_job_uuid,
                UUID,
            )
        ):
            raise TypeError(
                "retried_from_job_uuid must be a UUID or None"
            )
        if self.retried_from_job_uuid == self.job_uuid:
            raise ValueError(
                "a job cannot retry itself"
            )

        self._validate_datetime(
            self.created_at,
            "created_at",
            required=True,
        )
        self._validate_datetime(
            self.started_at,
            "started_at",
        )
        self._validate_datetime(
            self.completed_at,
            "completed_at",
        )
        self._validate_datetime(
            self.cancelled_at,
            "cancelled_at",
        )

        counters = (
            self.total,
            self.created,
            self.existing,
            self.failed,
        )
        if any(
            not isinstance(value, int)
            for value in counters
        ):
            raise TypeError("job counters must be integers")
        if any(value < 0 for value in counters):
            raise ValueError(
                "job counters must not be negative"
            )
        if self.total != len(self.celex):
            raise ValueError(
                "total must equal the CELEX item count"
            )
        if self.created + self.existing + self.failed > self.total:
            raise ValueError(
                "result counters must not exceed total"
            )

        if (
            self.status is ImportJobStatus.CANCELLED
            and self.cancelled_at is None
        ):
            raise ValueError(
                "cancelled jobs must define cancelled_at"
            )
        if (
            self.status is not ImportJobStatus.CANCELLED
            and self.cancelled_at is not None
        ):
            raise ValueError(
                "only cancelled jobs may define cancelled_at"
            )

    @classmethod
    def create(
        cls,
        celex: tuple[str, ...],
        *,
        created_at: datetime,
        retried_from_job_uuid: UUID | None = None,
    ) -> ImportJob:
        """Create a new pending import job."""
        return cls(
            job_uuid=uuid4(),
            celex=celex,
            status=ImportJobStatus.PENDING,
            created_at=created_at,
            retried_from_job_uuid=retried_from_job_uuid,
            total=len(celex),
        )

    @staticmethod
    def _validate_datetime(
        value: datetime | None,
        name: str,
        *,
        required: bool = False,
    ) -> None:
        if value is None:
            if required:
                raise TypeError(
                    f"{name} must be a datetime"
                )
            return
        if not isinstance(value, datetime):
            raise TypeError(
                f"{name} must be a datetime or None"
            )
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                f"{name} must be timezone-aware"
            )
