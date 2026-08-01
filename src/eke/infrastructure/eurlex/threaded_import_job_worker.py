"""Thread-pool adapter for import-job background execution."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from threading import RLock
from typing import Protocol
from uuid import UUID

from eke.application.eurlex import ImportJobWorker


class ImportJobRunner(Protocol):
    """Run one persistent import job by UUID."""

    def run_job(self, job_uuid: UUID) -> object:
        """Run one import job."""


class ThreadedImportJobWorker:
    """Execute import jobs in a bounded thread pool."""

    def __init__(
        self,
        runner: ImportJobRunner,
        *,
        max_workers: int = 2,
        thread_name_prefix: str = "eke-import-job",
    ) -> None:
        if not hasattr(runner, "run_job"):
            raise TypeError(
                "runner must implement run_job"
            )
        if not isinstance(max_workers, int):
            raise TypeError("max_workers must be an integer")
        if max_workers < 1:
            raise ValueError(
                "max_workers must be greater than zero"
            )
        if not isinstance(thread_name_prefix, str):
            raise TypeError(
                "thread_name_prefix must be a string"
            )
        if not thread_name_prefix.strip():
            raise ValueError(
                "thread_name_prefix must not be empty"
            )

        self._runner = runner
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
        )
        self._futures: dict[UUID, Future[object]] = {}
        self._lock = RLock()
        self._shutdown = False

    def submit(self, job_uuid: UUID) -> bool:
        """Submit a job unless it is already running."""
        if not isinstance(job_uuid, UUID):
            raise TypeError("job_uuid must be a UUID")

        with self._lock:
            if self._shutdown:
                raise RuntimeError(
                    "import job worker is shut down"
                )

            existing = self._futures.get(job_uuid)
            if existing is not None and not existing.done():
                return False

            future = self._executor.submit(
                self._runner.run_job,
                job_uuid,
            )
            self._futures[job_uuid] = future

            def callback(completed: Future[object]) -> None:
                self._forget(job_uuid, completed)

            future.add_done_callback(callback)

            return True

    def shutdown(self, *, wait: bool = True) -> None:
        """Stop accepting submissions and close the executor."""
        if not isinstance(wait, bool):
            raise TypeError("wait must be a boolean")

        with self._lock:
            if self._shutdown:
                return
            self._shutdown = True

        self._executor.shutdown(wait=wait)

    def _forget(
        self,
        job_uuid: UUID,
        completed: Future[object],
    ) -> None:
        with self._lock:
            current = self._futures.get(job_uuid)
            if current is completed:
                self._futures.pop(job_uuid, None)

    def __enter__(self) -> ThreadedImportJobWorker:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.shutdown()


import_job_worker_contract: type[ImportJobWorker]
import_job_worker_contract = ThreadedImportJobWorker
