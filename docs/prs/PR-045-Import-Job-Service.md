# PR-045 — Import Job Service

## Objective

Add application-level lifecycle management for persistent EUR-Lex import jobs.

## Added

- `BulkImportExecutor` structural port;
- `EurLexImportJobService`;
- job creation and lookup;
- `PENDING -> RUNNING` transition;
- terminal `COMPLETED`, `PARTIALLY_FAILED`, and `FAILED` states;
- serialized bulk results;
- state and missing-job exceptions;
- application tests;
- ADR-0040.

## Not included

- HTTP endpoints;
- container wiring;
- background workers;
- scheduling or retry policies.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(application): add import job service
```
