# PR-048 — Asynchronous Import Job Submission

## Objective

Connect the import-jobs API to the background worker without removing the
existing synchronous endpoint.

## Added

- `POST /imports/eurlex/jobs/{job_uuid}/submit`;
- `202 Accepted` submission response;
- worker dependency provider;
- shared worker lifecycle in the application container;
- graceful shutdown during FastAPI lifespan exit;
- duplicate and invalid-state conflict handling;
- API tests with service and worker overrides;
- ADR-0043.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(presentation): submit import jobs asynchronously
```
