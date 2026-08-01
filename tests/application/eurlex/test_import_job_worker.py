"""Tests for the import-job worker protocol."""

from uuid import UUID

from eke.application.eurlex import ImportJobWorker


class Worker:
    def submit(self, job_uuid: UUID) -> bool:
        return True

    def shutdown(self, *, wait: bool = True) -> None:
        del wait


def test_structural_worker_satisfies_protocol() -> None:
    assert isinstance(Worker(), ImportJobWorker)
