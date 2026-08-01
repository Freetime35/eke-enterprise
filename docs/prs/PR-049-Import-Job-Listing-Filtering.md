# PR-049 — Import Job Listing & Filtering

## Objective

Add stable paginated search for persistent EUR-Lex import jobs.

## Added

- search criteria and page application values;
- repository search contract;
- SQLAlchemy filtering and pagination;
- application-service search method;
- `GET /imports/eurlex/jobs`;
- status and creation-window filters;
- stable descending ordering;
- domain/application, repository, and API tests;
- ADR-0044.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(presentation): add import job search
```
