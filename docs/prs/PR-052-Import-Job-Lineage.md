# PR-052 — Import Job Lineage

Adds:

- `ImportJobLineage` application value;
- lineage traversal in `EurLexImportJobService`;
- missing-parent and cycle detection;
- `GET /imports/eurlex/jobs/{job_uuid}/lineage`;
- root, current, depth, and ordered lineage items;
- application and API tests;
- ADR-0047.

No migration is required.
