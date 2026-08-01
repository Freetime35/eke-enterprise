# PR-017 — ProvenanceRecord

## Objective

Introduce immutable source and acquisition traceability for canonical
resource data.

## Added

- `ProvenanceSource`
- `AcquisitionMethod`
- `ProvenanceRecord`
- Public exports from `eke.domain.provenance`
- Timezone-aware acquisition validation
- Optional checksum support
- Source, ownership, and method query behavior
- Unit tests
- ADR-0012

## Invariants

A ProvenanceRecord:

- belongs to one ResourceUUID;
- has one canonical source;
- has one non-empty source reference;
- uses a timezone-aware acquisition datetime;
- has one canonical acquisition method;
- may contain one non-empty checksum;
- is immutable, hashable, and comparable.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ProvenanceRecord business concept
```
