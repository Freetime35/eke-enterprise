# PR-010 — ResourceTitle

## Objective

Introduce a temporal, localized title concept for canonical resources.

## Added

- `ResourceTitle`
- Public export from `eke.domain.resources`
- Date validity behavior
- Language behavior
- Same-language overlap detection
- Unit tests
- ADR-0005

## Invariants

A ResourceTitle:

- contains one `LocalizedText`;
- contains one `ValidityPeriod`;
- defaults to a fully open validity period;
- is immutable, hashable, and comparable.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce ResourceTitle business concept
```
