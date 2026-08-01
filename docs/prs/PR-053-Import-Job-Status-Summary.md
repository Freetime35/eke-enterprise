# PR-053 — Import Job Status Summary

Adds:

- `ImportJobStatusSummary`;
- application-level aggregation for every job status;
- `GET /imports/eurlex/jobs/summary`;
- response schema with total and per-status counts;
- application and API tests;
- ADR-0048.

No migration or repository protocol change is required.
