# PR-025 — Unit of Work

## Objective

Introduce explicit transactional boundaries for Resource application use cases.

## Added

- Application `UnitOfWork` protocol
- `InMemoryUnitOfWork`
- `SQLAlchemyUnitOfWork`
- Session-aware SQLAlchemy repository support
- Transactional ResourceService
- Commit and rollback tests
- ADR-0020

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(application): introduce Unit of Work
```
