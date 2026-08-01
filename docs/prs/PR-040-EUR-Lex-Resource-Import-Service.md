# PR-040 — EUR-Lex Resource Import Service

## Objective

Orchestrate retrieval, metadata parsing, domain mapping, and atomic persistence
of one EUR-Lex Resource.

## Added

- `EurLexImportResult`;
- `EurLexResourceImportService`;
- EUR-Lex metadata-to-Resource mapper;
- conservative ResourceType and ResourceStatus mappings;
- localized title mapping;
- SHA-256 acquisition provenance;
- CELEX-based idempotence;
- application workflow and mapper tests;
- ADR-0035.

## Scope boundary

This PR does not overwrite an existing Resource and does not create EuroVoc
classifications without localized labels.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(application): add EUR-Lex Resource import
```
