# PR-046 — Import Jobs API

## Objective

Expose persistent EUR-Lex import jobs through FastAPI without adding background
execution.

## Added

- import-job request and response schemas;
- `POST /imports/eurlex/jobs`;
- `GET /imports/eurlex/jobs/{job_uuid}`;
- `POST /imports/eurlex/jobs/{job_uuid}/run`;
- application-container wiring;
- FastAPI dependency provider;
- OpenAPI tag and contract updates;
- API integration tests with dependency overrides;
- ADR-0041.

## Not included

- background tasks;
- queues or workers;
- retry policies;
- scheduling.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(presentation): add import jobs API
```
