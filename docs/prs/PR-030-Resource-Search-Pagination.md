# PR-030 — Resource Search & Pagination

## Objective

Add filtered, stable, paginated Resource collection retrieval.

## Added

- ResourceSearchCriteria
- ResourceSearchPage
- ResourceRepository.search
- In-memory search implementation
- SQLAlchemy search implementation
- ResourceService.search
- GET `/resources`
- IdentifierScheme, ResourceType, and ResourceStatus filters
- limit and offset pagination
- stable ResourceUUID ordering
- repository, application, and API tests
- ADR-0025

## Example

```text
GET /resources?status=IN_FORCE&resource_type=REGULATION&limit=20&offset=0
```

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(application): add Resource search and pagination
```
