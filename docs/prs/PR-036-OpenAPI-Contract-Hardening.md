# PR-036 — OpenAPI Contract Hardening

## Objective

Treat the generated OpenAPI document as a stable, tested public contract.

## Added

- deterministic operation-ID generation;
- documented OpenAPI tags for every public API group;
- stable application description;
- reusable API and validation error schemas;
- complete public-path contract tests;
- operation-ID uniqueness and stability tests;
- ADR-0031.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(presentation): harden OpenAPI contract
```
