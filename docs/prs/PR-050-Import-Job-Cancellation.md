# PR-050 — Import Job Cancellation

Adds:

- `CANCELLED` import-job status;
- `cancelled_at` domain timestamp;
- backward-compatible codec support;
- `EurLexImportJobService.cancel_job`;
- `POST /imports/eurlex/jobs/{job_uuid}/cancel`;
- domain, application, and API tests;
- ADR-0045.

No worker thread is forcefully interrupted.
