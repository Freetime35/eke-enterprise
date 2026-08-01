# PR-051 — Import Job Retry

Adds:

- `retried_from_job_uuid` lineage;
- backward-compatible codec support;
- `EurLexImportJobService.retry_job`;
- `POST /imports/eurlex/jobs/{job_uuid}/retry`;
- `201 Created` and `Location`;
- application and API tests;
- ADR-0046.

No database migration is required because import jobs use versioned JSON
payloads.
