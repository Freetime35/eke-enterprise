"""Integration tests for Alembic migrations."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import Engine, inspect

from eke.infrastructure.database import (
    create_alembic_config,
    create_sqlite_engine,
    current_revision,
    downgrade_database,
    upgrade_database,
)

HEAD_REVISION = "20260801_0002"


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    database_path = tmp_path / "migrations.db"
    return create_sqlite_engine(
        f"sqlite+pysqlite:///{database_path}"
    )


def test_upgrade_head_creates_expected_schema(
    engine: Engine,
) -> None:
    upgrade_database(engine)

    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == {
        "alembic_version",
        "import_jobs",
        "resource_identifiers",
        "resources",
    }
    assert current_revision(engine) == HEAD_REVISION

    resource_columns = {
        column["name"]
        for column in inspector.get_columns("resources")
    }
    assert resource_columns == {
        "resource_uuid",
        "payload_version",
        "payload",
        "created_at",
        "updated_at",
    }

    import_job_columns = {
        column["name"]
        for column in inspector.get_columns("import_jobs")
    }
    assert import_job_columns == {
        "job_uuid",
        "status",
        "payload_version",
        "payload",
        "created_at",
        "updated_at",
    }


def test_downgrade_base_removes_domain_tables(
    engine: Engine,
) -> None:
    upgrade_database(engine)
    downgrade_database(engine)

    assert set(inspect(engine).get_table_names()) == {
        "alembic_version"
    }
    assert current_revision(engine) is None


def test_upgrade_after_downgrade_is_reproducible(
    engine: Engine,
) -> None:
    upgrade_database(engine)
    downgrade_database(engine)
    upgrade_database(engine)

    assert current_revision(engine) == HEAD_REVISION
    assert "resources" in inspect(engine).get_table_names()
    assert "import_jobs" in inspect(engine).get_table_names()


def test_upgrade_is_idempotent_at_head(
    engine: Engine,
) -> None:
    upgrade_database(engine)
    upgrade_database(engine)

    assert current_revision(engine) == HEAD_REVISION


def test_configuration_resolves_project_migrations() -> None:
    config = create_alembic_config()

    script_location = Path(
        config.get_main_option("script_location")
    )
    assert script_location.name == "migrations"
    assert script_location.is_dir()


def test_invalid_migration_arguments_are_rejected(
    engine: Engine,
) -> None:
    with pytest.raises(
        TypeError,
        match="engine must be an Engine",
    ):
        upgrade_database(object())  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match="revision must be a string",
    ):
        upgrade_database(engine, 1)  # type: ignore[arg-type]

    with pytest.raises(
        ValueError,
        match="revision must not be empty",
    ):
        downgrade_database(engine, " ")

    with pytest.raises(
        TypeError,
        match="database_url must be a string or None",
    ):
        create_alembic_config(
            database_url=1,  # type: ignore[arg-type]
        )

    with pytest.raises(
        ValueError,
        match="database_url must not be empty",
    ):
        create_alembic_config(database_url=" ")
