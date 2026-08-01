# PR-014 — ResourceVersion

## Objective

Introduce canonical resource version identity and version behavior.

## Added

- `ResourceVersionUUID`
- `ResourceVersion`
- Public exports
- Resource ownership behavior
- Temporal validity behavior
- Lifecycle status behavior
- Direct predecessor behavior
- Unit tests
- ADR-0009

## Invariants

A ResourceVersion:

- has its own immutable identity;
- belongs to exactly one Resource;
- has one ResourceStatus;
- has one ValidityPeriod;
- may reference one previous version;
- cannot reference itself as its previous version.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ResourceVersion business concept
```
