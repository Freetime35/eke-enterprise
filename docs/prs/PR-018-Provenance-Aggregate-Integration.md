# PR-018 — Provenance Aggregate Integration

## Objective

Integrate immutable provenance records into the `Resource` aggregate.

## Added

- Provenance collection ownership
- Provenance member validation
- Duplicate provenance validation
- Resource ownership validation
- Query by ProvenanceSource
- Query by AcquisitionMethod
- Inclusive acquisition datetime range filtering
- Latest provenance lookup
- Aggregate integration tests
- ADR-0013

## Aggregate invariants

A Resource:

- stores provenance records as an immutable tuple;
- rejects exact duplicate provenance records;
- owns only records matching its ResourceUUID;
- allows repeated acquisitions of the same source reference when records
  are otherwise distinct.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): integrate provenance into Resource aggregate
```
