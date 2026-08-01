# PR-008 — LocalizedText

## Objective

Introduce an immutable value object for language-dependent legal and
regulatory text.

## Added

- `LocalizedText`
- Public export from `eke.domain.localization`
- Validation for language and non-empty text
- Language comparison behavior
- Unit tests
- ADR-0003

## Invariants

A LocalizedText:

- has exactly one `LanguageCode`;
- has one non-empty string value;
- preserves the supplied text exactly;
- is immutable;
- is hashable and comparable.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): introduce LocalizedText value object
```
