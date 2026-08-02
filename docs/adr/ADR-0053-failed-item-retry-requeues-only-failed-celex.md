# ADR-0053 — Failed-Item Retry Requeues Only Failed CELEX

**Status:** Accepted

Selective retry reads the persisted item-level result payload and extracts only
entries whose status is `FAILED`.

A new pending job is created with those CELEX identifiers and linked through
`retried_from_job_uuid`.

Selective retry is allowed only for `FAILED` and `PARTIALLY_FAILED` jobs.
Missing, malformed, or unusable item-level results produce a state conflict.

No migration is required because item results are already persisted in
`result_json`.
