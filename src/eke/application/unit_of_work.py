from __future__ import annotations

from types import TracebackType
from typing import Protocol, runtime_checkable

from eke.domain.repositories import ResourceRepository


@runtime_checkable
class UnitOfWork(Protocol):
    """Define an atomic application transaction boundary."""

    resources: ResourceRepository

    def __enter__(self) -> UnitOfWork:
        """Open the unit of work and return it."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Close the unit of work, rolling back when necessary."""

    def commit(self) -> None:
        """Commit all changes performed in the unit of work."""

    def rollback(self) -> None:
        """Roll back all uncommitted changes."""
