# ADR-0045 — Import Job Cancellation Is Limited to Pending Jobs

**Status:** Accepted

Import jobs may be cancelled only while their status is `PENDING`.

Python threads cannot be interrupted safely once execution begins. Therefore,
`RUNNING` jobs are not force-cancelled. Terminal jobs are also immutable.

Cancellation records:

- status `CANCELLED`;
- timezone-aware `cancelled_at`;
- no result counters or synthetic failure.

The API exposes:

```text
POST /imports/eurlex/jobs/{job_uuid}/cancel
```

It returns `404` for a missing job and `409` when the job is no longer pending.
