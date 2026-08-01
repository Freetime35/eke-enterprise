# PR-055 — Import Job Duration Statistics

Adds:

- `ImportJobDurationStatistics`;
- minimum, maximum, and average execution durations;
- paginated aggregation over terminal jobs;
- `GET /imports/eurlex/jobs/durations`;
- application and API tests;
- ADR-0050.

No migration or repository protocol change is required.
