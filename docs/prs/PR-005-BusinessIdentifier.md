# PR-005 — BusinessIdentifier

## Objective

Introduce an immutable value object representing an external business
identifier associated with a controlled identifier scheme.

## Added

- `BusinessIdentifier`
- Validation for identifier scheme and identifier value
- Tests for immutability, equality, hashing, and invalid values
- Public export from `eke.domain.identity`

## Design

`BusinessIdentifier` combines:

- one `IdentifierScheme`;
- one non-empty string value.

Scheme-specific syntax validation is intentionally excluded from this
value object and may be introduced later through dedicated policies or
validators.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Commit

```text
feat(domain): introduce BusinessIdentifier value object
```
