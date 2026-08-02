# PR-058 — Failed-Item Import Job Retry

Adds:

- failed-item extraction from persistent job results;
- selective retry in `EurLexImportJobService`;
- `POST /imports/eurlex/jobs/{job_uuid}/retry-failed`;
- lineage preservation;
- conflict handling for unusable results;
- application and API tests;
- OpenAPI contract coverage;
- ADR-0053.
