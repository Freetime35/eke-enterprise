# ADR-0051 — Stale Import Jobs Are Detected from Running Age

**Status:** Accepted

A job is considered stale when:

- its status is `RUNNING`;
- it defines `started_at`;
- its age is greater than or equal to a caller-provided threshold.

Detection scans paginated `RUNNING` jobs through the existing repository search
contract. No job state is changed automatically.

The API exposes:

```text
GET /imports/eurlex/jobs/stale?threshold_seconds=3600
```

The threshold is limited to 1 second through 7 days.
