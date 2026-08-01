# ADR-0043 — Import Job Submission Is Asynchronous and Additive

**Status:** Accepted

## Context

PR-047 introduced a replaceable background worker. The HTTP API still exposes
only synchronous execution through `/run`.

## Decision

The presentation layer SHALL add:

```text
POST /imports/eurlex/jobs/{job_uuid}/submit
```

The endpoint SHALL:

- verify that the job exists;
- require the job to remain `PENDING`;
- submit the UUID through `ImportJobWorker`;
- return `202 Accepted`;
- return `409` when the job is already submitted or not pending;
- return `404` when the job does not exist.

The existing synchronous `/run` endpoint SHALL remain available for backward
compatibility and deterministic administrative use.

The application container SHALL own one worker for the FastAPI lifespan and
shall shut it down during application shutdown.

## Consequences

- HTTP requests no longer need to block while an import runs.
- Existing clients using `/run` continue to work.
- Worker lifecycle is explicit and leak-free.
- In-process duplicate protection remains local to one application instance.
