# PR-037 — CELEX Identifier Parsing & Validation

## Objective

Introduce a domain value object for normalized, standard-form CELEX
identifiers before implementing EUR-Lex ingestion.

## Added

- `CelexSector`;
- immutable `CelexIdentifier`;
- parsing with optional `CELEX:` prefix;
- canonical uppercase rendering;
- structural accessors;
- conversion to `BusinessIdentifier`;
- positive and negative parser tests;
- ADR-0032.

## Scope boundary

This PR intentionally supports standard-form CELEX identifiers only.
Consolidated, corrigendum, and specialized historical variants remain future
explicit extensions.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(domain): add CELEX identifier parsing
```
