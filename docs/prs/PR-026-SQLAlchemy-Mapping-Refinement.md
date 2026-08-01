# PR-026 — SQLAlchemy Mapping Refinement

## Objective

Make the SQLAlchemy persistence schema stable, migration-ready, and
explicitly versioned.

## Added

- deterministic SQLAlchemy naming conventions;
- technical creation and update timestamps;
- Resource payload schema version;
- ORM relationship and delete-orphan cascade;
- explicit indexes;
- versioned Resource JSON envelope;
- legacy payload compatibility;
- mapping and codec tests;
- ADR-0021.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
refactor(infrastructure): refine SQLAlchemy mappings
```
