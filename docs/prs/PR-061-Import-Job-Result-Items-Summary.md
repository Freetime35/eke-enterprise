# PR-061 — Import Job Result Items Summary

Adds:

- aggregate item-result summary values;
- service-level result summary generation;
- `GET /imports/eurlex/jobs/{job_uuid}/items/summary`;
- counts and success/failure rates;
- application and API tests;
- OpenAPI contract coverage;
- ADR-0056.

No migration or repository protocol change is required.
