"""Import-job background execution port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class ImportJobWorker(Protocol):
    """Submit persistent import jobs for background execution."""

    def submit(self, job_uuid: UUID) -> bool:
        """Submit a job and report whether it was accepted."""

    def shutdown(self, *, wait: bool = True) -> None:
        """Stop accepting work and release worker resources."""
