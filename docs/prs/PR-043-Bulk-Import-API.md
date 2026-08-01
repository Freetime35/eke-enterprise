# PR-043 — Bulk Import API

Adds:

- `EurLexBulkImportService`;
- per-item bulk result models;
- duplicate removal with stable ordering;
- partial-success reporting;
- `POST /imports/eurlex/bulk`;
- maximum request size of 100 CELEX values;
- application and API tests;
- ADR-0038.

Validation:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
