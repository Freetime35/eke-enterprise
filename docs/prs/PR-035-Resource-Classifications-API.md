# PR-035 — Resource Classifications API

Adds:

- ResourceClassificationService;
- nested classification endpoints;
- classification DTOs and mappers;
- scheme-code-language uniqueness enforcement;
- duplicate and missing assignment handling;
- application and API tests;
- ADR-0030.

Validation:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
