# PR-032 — Resource Versions API

Adds:

- ResourceVersionService;
- nested version endpoints;
- version DTOs and mappers;
- history conflict validation;
- 404 and 409 error mappings;
- application and API tests;
- ADR-0027.

Validation:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
