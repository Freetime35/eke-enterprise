# ADR-0042 — Import Jobs Use a Bounded Thread-Pool Adapter

**Status:** Accepted

## Context

Persistent import jobs, lifecycle management, and HTTP endpoints now exist.
Background execution is required without coupling the application layer to a
specific queue product.

## Decision

The application layer SHALL define an `ImportJobWorker` protocol with:

- `submit(job_uuid)`;
- `shutdown(wait=True)`.

The infrastructure layer SHALL provide `ThreadedImportJobWorker`, backed by a
bounded `ThreadPoolExecutor`.

The worker SHALL:

- delegate all lifecycle rules to `EurLexImportJobService.run_job`;
- reject duplicate submissions while the same job is still running;
- allow resubmission after completion;
- reject submissions after shutdown;
- support deterministic resource cleanup.

PR-047 SHALL not change the public HTTP API and SHALL not add a distributed
queue, scheduler, retry policy, or recurring polling loop.

## Consequences

- Background execution is available through a replaceable adapter.
- Application code remains independent of threads.
- Duplicate concurrent execution is prevented in one process.
- Multi-process coordination remains a future concern.
