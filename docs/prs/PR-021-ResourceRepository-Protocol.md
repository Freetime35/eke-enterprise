# PR-021 — ResourceRepository Protocol

## Objective

Introduce the first persistence contract for Resource aggregates without
adding any database dependency to the domain.

## Added

- `ResourceRepository`
- Runtime-checkable structural protocol
- Save, lookup, existence, and deletion operations
- Lookup by internal and business identifier
- In-memory contract tests
- ADR-0016

## Contract

A ResourceRepository provides:

- `save(resource)`
- `get(resource_uuid)`
- `get_by_identifier(identifier)`
- `exists(resource_uuid)`
- `delete(resource_uuid)`

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ResourceRepository protocol
```
