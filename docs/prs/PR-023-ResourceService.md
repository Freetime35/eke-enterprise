# PR-023 — ResourceService

## Objective

Introduce the first application-layer service for Resource use cases.

## Added

- `ResourceService`
- Application-layer exceptions
- Create, get, find, update, delete, and exists use cases
- Duplicate identity and identifier protection
- Repository abstraction dependency
- Application service tests
- ADR-0018

## Public operations

- `create(resource)`
- `get(resource_uuid)`
- `find_by_identifier(identifier)`
- `update(resource)`
- `delete(resource_uuid)`
- `exists(resource_uuid)`

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(application): add ResourceService
```
