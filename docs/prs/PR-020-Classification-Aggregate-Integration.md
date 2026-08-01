# PR-020 — Classification Aggregate Integration

## Objective

Integrate canonical classification concepts into the `Resource`
aggregate.

## Added

- Classification collection ownership
- Classification member validation
- Exact duplicate validation
- Scheme-code-language uniqueness validation
- Query by ClassificationScheme
- Query by scheme and code
- Query by label language
- Query by temporal validity
- Aggregate integration tests
- ADR-0015

## Aggregate invariants

A Resource:

- stores classifications as an immutable tuple;
- rejects exact duplicate classifications;
- rejects repeated scheme, code, and language combinations;
- permits multilingual labels for the same scheme and code;
- permits the same code in different schemes.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): integrate classifications into Resource aggregate
```
