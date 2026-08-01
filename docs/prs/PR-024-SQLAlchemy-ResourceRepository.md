# PR-024 — SQLAlchemy ResourceRepository

## Objective

Add the first durable ResourceRepository adapter using SQLAlchemy 2.x and SQLite.

## Added

- SQLAlchemy declarative base and session factory
- SQLite engine helper
- ORM resource and identifier-index models
- Canonical Resource JSON codec
- SQLAlchemyResourceRepository
- SQLite integration tests
- ADR-0019

## Dependency

Add the following runtime dependency to `pyproject.toml`:

```toml
dependencies = [
    "SQLAlchemy>=2.0,<3.0",
]
```

If `dependencies` already contains entries, append the SQLAlchemy entry.

## Validation

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): add SQLAlchemy ResourceRepository
```
