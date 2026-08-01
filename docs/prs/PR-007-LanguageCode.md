# PR-007 — LanguageCode

## Objective

Introduce the canonical language code value object used by multilingual
domain concepts.

## Added

- `LanguageCode`
- Public export from `eke.domain.localization`
- Syntax validation and lowercase normalization
- Uppercase conversion for source-system interoperability
- Unit tests
- ADR-0002

## Invariants

A LanguageCode:

- contains exactly two ASCII alphabetic characters;
- is stored in lowercase;
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
feat(domain): introduce LanguageCode value object
```
