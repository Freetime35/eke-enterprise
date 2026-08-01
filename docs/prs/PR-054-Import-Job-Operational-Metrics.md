# PR-054 — Import Job Operational Metrics

Adds:

- `ImportJobOperationalMetrics`;
- deterministic derivation from PR-053 status summaries;
- `GET /imports/eurlex/jobs/metrics`;
- active, terminal, successful, unsuccessful, and cancelled counters;
- completion and failure rates;
- application and API tests;
- ADR-0049.

No migration or repository protocol change is required.
