# ADR-0049 — Import Job Metrics Are Derived from Status Summary

**Status:** Accepted

Operational metrics are derived from the complete status summary introduced in
PR-053.

The metrics are:

- total jobs;
- active jobs (`PENDING` + `RUNNING`);
- terminal jobs;
- successful jobs (`COMPLETED`);
- unsuccessful jobs (`FAILED` + `PARTIALLY_FAILED`);
- cancelled jobs;
- completion rate among terminal jobs;
- failure rate among terminal jobs.

No repository method, migration, Prometheus dependency, or external monitoring
backend is introduced.
