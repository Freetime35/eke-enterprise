# ADR-0038 — Bulk Import Reports Partial Success

**Status:** Accepted

Bulk EUR-Lex import is an orchestration concern over the existing idempotent
single-resource import service.

A bulk request accepts at most 100 CELEX identifiers, removes duplicates while
preserving request order, and processes each unique identifier independently.

The operation returns `200 OK` with one result per unique CELEX:

- `CREATED`;
- `EXISTING`;
- `FAILED`.

A failure for one CELEX does not roll back successful imports for other CELEX
values, because each single import owns its own Unit of Work. Request-level
validation errors still return `422`.
