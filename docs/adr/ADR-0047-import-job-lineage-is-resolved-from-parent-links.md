# ADR-0047 — Import Job Lineage Is Resolved from Parent Links

**Status:** Accepted

Retry lineage is reconstructed by following each job's
`retried_from_job_uuid` link from the requested job back to the root.

The application service returns lineage ordered from root to current job.

Missing parents and cycles are treated as persisted-data conflicts.

No reverse child index or database migration is introduced because PR-052
only needs ancestor lineage for one requested job.
