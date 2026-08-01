# PR-044 — Import Job Persistence

## Objective

Add the persistent import-job foundation without execution or presentation
concerns.

## Added

- `ImportJob` and `ImportJobStatus`;
- `ImportJobRepository` protocol;
- versioned JSON codec;
- `ImportJobModel`;
- `SQLAlchemyImportJobRepository`;
- Alembic revision `20260801_0002`;
- domain, codec, repository, and migration tests;
- ADR-0039.

## Not included

- import job service;
- job execution;
- HTTP endpoints;
- background workers.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): add import job persistence
```
