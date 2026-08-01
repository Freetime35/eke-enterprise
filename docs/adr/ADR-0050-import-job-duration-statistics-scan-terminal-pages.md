# ADR-0050 — Import Job Duration Statistics Scan Terminal Pages

**Status:** Accepted

Execution duration statistics are computed from terminal jobs that define both
`started_at` and `completed_at`.

The application service scans paginated search results for:

- `COMPLETED`;
- `PARTIALLY_FAILED`;
- `FAILED`.

Cancelled jobs are excluded because they never started. Jobs with incomplete
timestamps are ignored.

The API exposes:

```text
GET /imports/eurlex/jobs/durations
```

No repository protocol change, migration, or external metrics backend is
introduced.
