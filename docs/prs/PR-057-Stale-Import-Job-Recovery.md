# PR-057 — Stale Import Job Recovery

Adds:

- explicit stale-job recovery in `EurLexImportJobService`;
- `POST /imports/eurlex/jobs/{job_uuid}/recover-stale`;
- configurable threshold validation;
- `404`, `409`, and `422` behavior;
- application and API tests;
- OpenAPI contract coverage;
- ADR-0052.

No migration, new status, or repository protocol change is required.
