# PR-016 — ResourceRelationship Aggregate Integration

## Objective

Integrate canonical outgoing relationships into the `Resource`
aggregate.

## Added

- Relationship collection ownership
- Relationship member validation
- Duplicate relationship validation
- Outgoing direction validation
- Query by RelationshipType
- Query by target ResourceUUID
- Query by active date
- Aggregate integration tests
- ADR-0011

## Aggregate invariants

A Resource:

- owns only relationships originating from its own ResourceUUID;
- stores relationships as an immutable tuple;
- rejects exact duplicate relationships;
- allows distinct relationship types to the same target.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): integrate relationships into Resource aggregate
```
