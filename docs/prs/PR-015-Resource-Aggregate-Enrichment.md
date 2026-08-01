# PR-015 — Resource Aggregate Enrichment

## Objective

Enrich the `Resource` aggregate with canonical type, lifecycle status,
localized titles, and resource versions.

## Added

- Resource type and status ownership
- Title collection ownership and validation
- Version collection ownership and validation
- Language-specific title queries
- Date-specific title lookup
- Version identity lookup
- Date-specific version filtering
- Aggregate enrichment tests
- ADR-0010

## Aggregate invariants

A Resource:

- preserves all previous identifier invariants;
- has one ResourceType and ResourceStatus;
- rejects overlapping same-language titles;
- rejects duplicate version identities;
- owns every included ResourceVersion;
- requires referenced previous versions to exist in the aggregate.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): enrich Resource aggregate
```
