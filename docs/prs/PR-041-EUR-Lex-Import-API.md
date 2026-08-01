# PR-041 — EUR-Lex Import API

## Objective

Expose the idempotent EUR-Lex Resource import workflow through FastAPI.

## Added

- `POST /imports/eurlex`;
- request and response schemas;
- dynamic `201 Created` / `200 OK` behavior;
- canonical Resource `Location` header;
- EUR-Lex import dependency wiring;
- shared HTTP client lifecycle management;
- 404 and 502 exception mappings;
- API integration tests with dependency overrides;
- OpenAPI tag, path, and operation-ID updates;
- ADR-0036.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(presentation): add EUR-Lex import API
```
