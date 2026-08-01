# PR-027 — Alembic Migrations

## Objective

Introduce version-controlled and reversible database schema migrations.

## Added

- Alembic development dependency
- `alembic.ini`
- migration environment using `Base.metadata`
- initial Resource persistence revision
- programmatic migration helpers
- upgrade, downgrade, idempotency, and reproducibility tests
- ADR-0022

## Commands

```bash
alembic upgrade head
alembic current
alembic downgrade base
```

The default URL in `alembic.ini` targets:

```text
sqlite+pysqlite:///eke-enterprise.db
```

## Validation

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): add Alembic migrations
```
