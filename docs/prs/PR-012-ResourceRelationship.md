# PR-012 — ResourceRelationship

## Objective

Introduce the canonical directed relationship concept between resources.

## Added

- `RelationshipType`
- `ResourceRelationship`
- Public exports from `eke.domain.relationships`
- Direction behavior
- Connectivity behavior
- Temporal validity behavior
- Unit tests
- ADR-0007

## Invariants

A ResourceRelationship:

- has one source `ResourceUUID`;
- has one target `ResourceUUID`;
- uses one `RelationshipType`;
- has one `ValidityPeriod`;
- rejects identical source and target identities;
- is immutable, hashable, and comparable.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ResourceRelationship business concept
```
