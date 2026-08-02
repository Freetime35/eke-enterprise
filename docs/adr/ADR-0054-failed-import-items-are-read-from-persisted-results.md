# ADR-0054 — Failed Import Items Are Read from Persisted Results

**Status:** Accepted

Failed-item inspection reads the item-level payload already stored in
`ImportJob.result_json`.

The application exposes structured values containing:

- `celex`;
- `error_code`;
- `detail`.

Inspection is limited to `FAILED` and `PARTIALLY_FAILED` jobs. Missing,
malformed, or empty failed-item results produce a state conflict.

No migration or repository protocol change is required.
