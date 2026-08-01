# PR-006 — Resource Aggregate Root

## Objective

Introduce the first aggregate root of the EKE Enterprise canonical
domain model.

## Added

- `Resource`
- Resource package public export
- Aggregate invariant validation
- Identifier lookup behavior
- Behavioral unit tests
- ADR-0001

## Aggregate invariants

A Resource:

- has exactly one `ResourceUUID`;
- has at least one `BusinessIdentifier`;
- accepts identifiers only as an immutable tuple;
- rejects duplicate identifiers;
- rejects multiple identifiers for the same scheme.

## Public behavior

- `has_identifier`
- `find_identifier`
- `has_identifier_scheme`

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce Resource aggregate root
```
