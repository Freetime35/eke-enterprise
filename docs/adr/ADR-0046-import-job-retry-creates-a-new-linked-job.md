# ADR-0046 — Import Job Retry Creates a New Linked Job

**Status:** Accepted

Retrying an import job SHALL create a new `PENDING` job rather than resetting
the original record.

The new job copies the original CELEX list and stores
`retried_from_job_uuid`.

Retry is allowed only for:

- `FAILED`;
- `PARTIALLY_FAILED`;
- `CANCELLED`.

`COMPLETED`, `PENDING`, and `RUNNING` jobs cannot be retried.

This preserves audit history and avoids mutating terminal job outcomes.
