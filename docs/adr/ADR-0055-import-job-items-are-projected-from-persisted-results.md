# ADR-0055 — Import Job Items Are Projected from Persisted Results

**Status:** Accepted

Item-level import results are parsed from the existing
`ImportJob.result_json` payload.

The projection exposes:

- `celex`;
- `status`;
- `resource_uuid`;
- `error_code`;
- `detail`.

Inspection is limited to terminal jobs. A valid status filter may
return an empty result set. No migration or repository protocol
change is required.
