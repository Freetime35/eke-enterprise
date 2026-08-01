# PR-013 — ResourceStatus

## Objective

Introduce the canonical lifecycle vocabulary used by resources.

## Added

- `ResourceStatus`
- Public export from `eke.domain.resources`
- Terminal-state behavior
- Effective-state behavior
- Pre-effective-state behavior
- Unit tests
- ADR-0008

## Supported values

- DRAFT
- ADOPTED
- PUBLISHED
- IN_FORCE
- PARTIALLY_IN_FORCE
- NOT_YET_IN_FORCE
- REPEALED
- EXPIRED
- WITHDRAWN
- ANNULLED
- SUPERSEDED
- UNKNOWN

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ResourceStatus enumeration
```
