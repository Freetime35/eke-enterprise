# PR-034 — Resource Provenance API

Adds:

- ResourceProvenanceService;
- immutable nested provenance endpoints;
- provenance DTOs and mappers;
- timezone-aware acquisition validation;
- duplicate and missing record handling;
- application and API tests;
- ADR-0029.

Validation:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
