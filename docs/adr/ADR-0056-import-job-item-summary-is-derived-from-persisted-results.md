# ADR-0056 — Import Job Item Summary Is Derived from Persisted Results

**Status:** Accepted

Item-level summaries are derived from parsed `ImportJob.result_json`
values rather than stored as additional database columns.

The summary always exposes counts for `CREATED`, `EXISTING`, and
`FAILED`, including zero values. Success combines `CREATED` and
`EXISTING`; failure corresponds to `FAILED`.

Empty valid result lists produce zero counts and zero rates. No
migration or repository protocol change is required.
