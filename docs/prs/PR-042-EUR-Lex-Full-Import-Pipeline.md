# PR-042 — EUR-Lex Full Import Pipeline

Adds complete aggregate enrichment during import:

- initial ResourceVersion;
- labeled EuroVoc classifications;
- CELEX relationship resolution;
- minimal related Resource creation;
- existing acquisition provenance;
- atomic persistence in one Unit of Work;
- full-pipeline tests;
- ADR-0037.

Validation:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```
