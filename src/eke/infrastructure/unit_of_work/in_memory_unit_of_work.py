from __future__ import annotations

from types import TracebackType

from eke.domain.identity import ResourceUUID
from eke.domain.resources import Resource
from eke.infrastructure.repositories import InMemoryResourceRepository


class InMemoryUnitOfWork:
    """Provide atomic in-memory Resource operations for tests."""

    def __init__(
        self,
        repository: InMemoryResourceRepository | None = None,
    ) -> None:
        self.resources = repository or InMemoryResourceRepository()
        self._snapshot: dict[ResourceUUID, Resource] | None = None
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> InMemoryUnitOfWork:
        self._snapshot = dict(self.resources._resources)
        self.committed = False
        self.rolled_back = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        if exc_type is not None or not self.committed:
            self.rollback()
        return None

    def commit(self) -> None:
        self.committed = True
        self._snapshot = None

    def rollback(self) -> None:
        if self._snapshot is not None:
            self.resources._resources.clear()
            self.resources._resources.update(self._snapshot)
        self.rolled_back = True
        self._snapshot = None
    