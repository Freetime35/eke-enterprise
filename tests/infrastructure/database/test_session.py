from __future__ import annotations

import pytest
from sqlalchemy import text

from eke.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    session_scope,
)


def test_create_sqlite_engine_and_session_factory() -> None:
    engine = create_sqlite_engine()
    factory = create_session_factory(engine)

    with factory() as session:
        assert session.scalar(text("select 1")) == 1


def test_session_scope_commits() -> None:
    engine = create_sqlite_engine()
    factory = create_session_factory(engine)

    with session_scope(factory) as session:
        session.execute(text("create table example (value integer)"))
        session.execute(text("insert into example values (1)"))

    with factory() as session:
        assert session.scalar(text("select count(*) from example")) == 1


def test_invalid_configuration_inputs_are_rejected() -> None:
    with pytest.raises(TypeError, match="url must be a string"):
        create_sqlite_engine(1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="url must not be empty"):
        create_sqlite_engine(" ")
    with pytest.raises(TypeError, match="engine must be an Engine"):
        create_session_factory(object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="factory must be a sessionmaker"):
        with session_scope(object()):  # type: ignore[arg-type]
            pass
