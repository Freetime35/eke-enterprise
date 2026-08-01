# PR-009 — ValidityPeriod

## Objective

Introduce the canonical immutable date interval used by temporal domain
concepts.

## Added

- `ValidityPeriod`
- Public export from `eke.domain.temporal`
- Open and bounded period support
- Inclusive date containment
- Period overlap behavior
- Unit tests
- ADR-0004

## Invariants

A ValidityPeriod:

- uses `date` boundaries or `None`;
- permits open start and open end boundaries;
- rejects a start later than its end;
- treats boundaries as inclusive;
- is immutable, hashable, and comparable.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ValidityPeriod value object
```
