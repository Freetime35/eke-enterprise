# ADR-0044 — Import Job Search Uses Stable Offset Pagination

**Status:** Accepted

## Context

Import jobs can now be created, executed, submitted asynchronously, and
retrieved individually. Operators also need a stable way to list recent jobs
and isolate failed or running work.

## Decision

The application layer SHALL define:

- `ImportJobSearchCriteria`;
- `ImportJobSearchPage`;
- `ImportJobRepository.search(...)`;
- `EurLexImportJobService.search_jobs(...)`.

The API SHALL expose `GET /imports/eurlex/jobs` with optional filters:

- `status`;
- `created_from`;
- `created_to`;
- `limit`;
- `offset`.

Results SHALL be ordered by:

```text
created_at DESC, job_uuid DESC
```

The limit SHALL be between 1 and 100. Date filters SHALL be timezone-aware and
the lower bound SHALL not be after the upper bound.

## Consequences

- Operators can inspect recent and failed jobs.
- Pagination is deterministic for a fixed dataset.
- The collection path supports both `POST` creation and `GET` search.
- Cursor pagination can be introduced later without changing job identity.
