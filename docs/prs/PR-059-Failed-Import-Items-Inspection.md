# PR-059 — Failed Import Items Inspection

Adds:

- structured failed import-item values;
- service-level failed-item inspection;
- `GET /imports/eurlex/jobs/{job_uuid}/failed-items`;
- response schemas for failed items;
- application and API tests;
- OpenAPI contract coverage;
- ADR-0054.

No migration or repository protocol change is required.
