# PR-047 — Import Job Worker

## Objective

Add replaceable background execution for persistent import jobs without
changing the public HTTP API.

## Added

- `ImportJobWorker` application protocol;
- `ThreadedImportJobWorker`;
- bounded `ThreadPoolExecutor`;
- duplicate in-flight submission protection;
- graceful shutdown and context-manager support;
- application protocol tests;
- deterministic infrastructure tests;
- ADR-0042.

## Not included

- API changes;
- distributed queues;
- polling schedulers;
- retry policies;
- multi-process locking.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): add import job worker
```
