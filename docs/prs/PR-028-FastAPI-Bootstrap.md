# PR-028 — FastAPI Bootstrap

## Objective

Introduce an executable HTTP presentation adapter and composition root.

## Added

- FastAPI and Uvicorn runtime dependencies
- HTTPX development dependency
- immutable API settings
- application container
- FastAPI dependency providers
- lifespan-based database initialization
- automatic Alembic upgrade at startup
- `/health`
- `/ready`
- OpenAPI and interactive documentation bootstrap
- HTTP and settings tests
- ADR-0023

## Run locally

```bash
python -m uvicorn eke.presentation.api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ready
http://127.0.0.1:8000/docs
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
feat(presentation): bootstrap FastAPI application
```
