# PR-029 — Resource API CRUD

## Objective

Expose the first Resource application use cases through HTTP.

## Added

- Resource request and response DTOs
- HTTP/domain mappers
- POST `/resources`
- GET `/resources/{resource_uuid}`
- GET `/resources/by-identifier`
- PUT `/resources/{resource_uuid}`
- DELETE `/resources/{resource_uuid}`
- 404 and 409 application exception mapping
- CRUD integration tests
- Mapper tests
- ADR-0024

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(presentation): add Resource CRUD API
```
