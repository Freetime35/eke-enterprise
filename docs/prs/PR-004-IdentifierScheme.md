# PR-004 — IdentifierScheme

## Objective

Introduce the controlled vocabulary used to identify external business
identifier schemes supported by EKE Enterprise.

## Added

- `IdentifierScheme`
- Tests for all supported identifier schemes
- Public export from `eke.domain.identity`

## Supported schemes

- CELEX
- ELI
- CELLAR
- ECLI
- EURLEX

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Commit

```text
feat(domain): introduce IdentifierScheme enumeration
```
