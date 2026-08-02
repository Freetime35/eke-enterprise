# PR-056 — Stale Import Job Detection

Adds:

- `StaleImportJob`;
- `StaleImportJobReport`;
- paginated detection of old `RUNNING` jobs;
- configurable threshold;
- `GET /imports/eurlex/jobs/stale`;
- application and API tests;
- ADR-0051.

No migration, repository protocol change, or automatic recovery is included.
