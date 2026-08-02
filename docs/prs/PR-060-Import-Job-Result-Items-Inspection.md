# PR-060 — Import Job Result Items Inspection

Adds:

- generic persisted result-item parsing;
- service-level item inspection with optional status filtering;
- `GET /imports/eurlex/jobs/{job_uuid}/items`;
- item response schemas;
- application and API tests;
- OpenAPI contract coverage;
- ADR-0055.

No migration or repository protocol change is required.
