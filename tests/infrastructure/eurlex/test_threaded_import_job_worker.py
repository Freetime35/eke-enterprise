"""Tests for thread-pool import-job execution."""

from __future__ import annotations

from threading import Event, Lock
from uuid import UUID, uuid4

import pytest

from eke.application.eurlex import ImportJobWorker
from eke.infrastructure.eurlex import (
    ThreadedImportJobWorker,
)


class BlockingRunner:
    def __init__(self) -> None:
        self.started = Event()
        self.release = Event()
        self.calls: list[UUID] = []
        self._lock = Lock()

    def run_job(self, job_uuid: UUID) -> object:
        with self._lock:
            self.calls.append(job_uuid)
        self.started.set()
        self.release.wait(timeout=2)
        return object()


class ImmediateRunner:
    def __init__(self) -> None:
        self.calls: list[UUID] = []
        self.finished = Event()

    def run_job(self, job_uuid: UUID) -> object:
        self.calls.append(job_uuid)
        self.finished.set()
        return object()


def test_worker_satisfies_protocol() -> None:
    worker = ThreadedImportJobWorker(
        ImmediateRunner()
    )
    try:
        assert isinstance(worker, ImportJobWorker)
    finally:
        worker.shutdown()


def test_submit_executes_job_in_background() -> None:
    runner = ImmediateRunner()
    job_uuid = uuid4()

    with ThreadedImportJobWorker(runner) as worker:
        accepted = worker.submit(job_uuid)
        assert runner.finished.wait(timeout=2)

    assert accepted
    assert runner.calls == [job_uuid]


def test_duplicate_running_job_is_rejected() -> None:
    runner = BlockingRunner()
    job_uuid = uuid4()

    with ThreadedImportJobWorker(runner) as worker:
        assert worker.submit(job_uuid)
        assert runner.started.wait(timeout=2)
        assert not worker.submit(job_uuid)
        runner.release.set()

    assert runner.calls == [job_uuid]


def test_completed_job_can_be_submitted_again() -> None:
    runner = ImmediateRunner()
    job_uuid = uuid4()

    with ThreadedImportJobWorker(runner) as worker:
        assert worker.submit(job_uuid)
        assert runner.finished.wait(timeout=2)

        runner.finished.clear()
        assert worker.submit(job_uuid)
        assert runner.finished.wait(timeout=2)

    assert runner.calls == [job_uuid, job_uuid]


def test_submit_after_shutdown_is_rejected() -> None:
    worker = ThreadedImportJobWorker(
        ImmediateRunner()
    )
    worker.shutdown()

    with pytest.raises(
        RuntimeError,
        match="worker is shut down",
    ):
        worker.submit(uuid4())


def test_worker_validates_configuration() -> None:
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        ThreadedImportJobWorker(
            ImmediateRunner(),
            max_workers=0,
        )
