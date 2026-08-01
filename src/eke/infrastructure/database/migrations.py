"""Programmatic Alembic migration helpers."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine


def create_alembic_config(
    *,
    database_url: str | None = None,
    config_path: Path | None = None,
) -> Config:
    """Create an Alembic configuration for this repository."""
    if database_url is not None:
        if not isinstance(database_url, str):
            raise TypeError("database_url must be a string or None")
        if not database_url.strip():
            raise ValueError("database_url must not be empty")

    if config_path is not None and not isinstance(
        config_path,
        Path,
    ):
        raise TypeError("config_path must be a Path or None")

    project_root = Path(__file__).resolve().parents[4]
    resolved_config_path = (
        config_path
        if config_path is not None
        else project_root / "alembic.ini"
    )

    config = Config(str(resolved_config_path))
    config.set_main_option(
        "script_location",
        str(project_root / "migrations"),
    )

    if database_url is not None:
        config.set_main_option("sqlalchemy.url", database_url)

    return config


def upgrade_database(
    engine: Engine,
    revision: str = "head",
) -> None:
    """Upgrade a database to an Alembic revision."""
    _validate_engine_and_revision(engine, revision)
    config = create_alembic_config()

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def downgrade_database(
    engine: Engine,
    revision: str = "base",
) -> None:
    """Downgrade a database to an Alembic revision."""
    _validate_engine_and_revision(engine, revision)
    config = create_alembic_config()

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, revision)


def current_revision(engine: Engine) -> str | None:
    """Return the database's current Alembic revision."""
    if not isinstance(engine, Engine):
        raise TypeError("engine must be an Engine")

    config = create_alembic_config()
    revisions: list[str | None] = []

    with engine.begin() as connection:
        config.attributes["connection"] = connection

        def capture_revision(
            revision: tuple[str, ...],
            _context: object,
        ) -> None:
            revisions.append(revision[0] if revision else None)

        command.current(
            config,
            verbose=False,
            check_heads=False,
        )

        result = connection.exec_driver_sql(
            "SELECT version_num FROM alembic_version"
        ).scalar_one_or_none()

    return str(result) if result is not None else None


def _validate_engine_and_revision(
    engine: Engine,
    revision: str,
) -> None:
    if not isinstance(engine, Engine):
        raise TypeError("engine must be an Engine")
    if not isinstance(revision, str):
        raise TypeError("revision must be a string")
    if not revision.strip():
        raise ValueError("revision must not be empty")
