from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def create_sqlite_engine(url: str = "sqlite+pysqlite:///:memory:") -> Engine:
    """Create a SQLite engine suitable for development and tests."""
    if not isinstance(url, str):
        raise TypeError("url must be a string")
    if not url.strip():
        raise ValueError("url must not be empty")

    if url.endswith(":memory:"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_engine(url)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a configured SQLAlchemy session factory."""
    if not isinstance(engine, Engine):
        raise TypeError("engine must be an Engine")

    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope(
    factory: sessionmaker[Session],
) -> Iterator[Session]:
    """Provide a transactional session scope."""
    if not isinstance(factory, sessionmaker):
        raise TypeError("factory must be a sessionmaker")

    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
