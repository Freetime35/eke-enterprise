# PR-019 — ClassificationConcept

## Objective

Introduce canonical classification concepts with scheme, code, localized
label, and temporal validity.

## Added

- `ClassificationScheme`
- `ClassificationConcept`
- Public exports from `eke.domain.classification`
- Scheme, code, language, and date query behavior
- Unit tests
- ADR-0014

## Invariants

A ClassificationConcept:

- belongs to one ClassificationScheme;
- has one non-empty preserved code;
- has one LocalizedText label;
- has one ValidityPeriod;
- is immutable, hashable, and comparable.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ClassificationConcept value object
```
