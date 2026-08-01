"""Import job persistence port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from eke.domain.imports import ImportJob


@runtime_checkable
class ImportJobRepository(Protocol):
    """Persist and retrieve import jobs."""

    def save(self, job: ImportJob) -> None:
        """Create or replace an import job."""

    def get(self, job_uuid: UUID) -> ImportJob | None:
        """Return one import job, or None."""

    def exists(self, job_uuid: UUID) -> bool:
        """Return whether an import job exists."""
