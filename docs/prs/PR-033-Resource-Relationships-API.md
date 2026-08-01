# PR-033 — Resource Relationships API

Adds:

- ResourceRelationshipService;
- directed nested relationship endpoints;
- relationship DTOs and mappers;
- target existence validation;
- duplicate and missing relationship handling;
- application and API tests;
- ADR-0028.

Validation:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
