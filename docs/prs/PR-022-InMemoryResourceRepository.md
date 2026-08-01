# PR-022 — InMemoryResourceRepository

## Objective

Introduce the first concrete `ResourceRepository` implementation outside
the domain layer.

## Added

- `InMemoryResourceRepository`
- Infrastructure package structure
- Thread-safe repository operations
- Save and replacement behavior
- Lookup by internal and business identifier
- Existence and deletion behavior
- Clear and count conveniences
- Protocol conformance tests
- State-isolation tests
- Concurrent-save test
- ADR-0017

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): add InMemoryResourceRepository
```
