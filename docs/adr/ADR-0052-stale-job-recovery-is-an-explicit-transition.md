# ADR-0052 — Stale Job Recovery Is an Explicit Transition

**Status:** Accepted

A stale import job is recovered only through an explicit command.

The transition is:

```text
RUNNING -> FAILED
```

Recovery is allowed only when:

- the job exists;
- its status is `RUNNING`;
- it defines `started_at`;
- its age is greater than or equal to the supplied threshold.

Recovery persists:

- `status = FAILED`;
- `completed_at = current time`;
- `failed = total`;
- `error_detail = "import job exceeded stale threshold"`.

The operation does not interrupt a worker thread. It only repairs persistent
state after an abandoned or lost execution.
