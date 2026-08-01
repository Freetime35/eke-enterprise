from __future__ import annotations

from types import TracebackType

from sqlalchemy.orm import Session, sessionmaker

from eke.infrastructure.repositories import SQLAlchemyResourceRepository


class SQLAlchemyUnitOfWork:
    """Manage one SQLAlchemy Session per application transaction."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        if not isinstance(session_factory, sessionmaker):
            raise TypeError("session_factory must be a sessionmaker")
        self._session_factory = session_factory
        self._session: Session | None = None
        self.resources: SQLAlchemyResourceRepository

    def __enter__(self) -> SQLAlchemyUnitOfWork:
        if self._session is not None:
            raise RuntimeError("unit of work is already active")
        self._session = self._session_factory()
        self.resources = SQLAlchemyResourceRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        try:
            if exc_type is not None:
                self.rollback()
            elif self._session is not None and self._session.in_transaction():
                self.rollback()
        finally:
            if self._session is not None:
                self._session.close()
                self._session = None
        return None

    def commit(self) -> None:
        session = self._require_session()
        session.commit()

    def rollback(self) -> None:
        session = self._require_session()
        session.rollback()

    def _require_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("unit of work is not active")
        return self._session
    
