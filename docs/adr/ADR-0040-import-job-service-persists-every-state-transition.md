# ADR-0040 — Import Job Service Persists Every State Transition

**Status:** Accepted

## Context

PR-044 introduced durable import jobs and a repository port. Application
orchestration is now required without coupling job execution to FastAPI,
SQLAlchemy, or background workers.

## Decision

The application layer SHALL provide `EurLexImportJobService`.

The service SHALL:

- create a deduplicated `PENDING` job;
- retrieve jobs by UUID;
- allow execution only from `PENDING`;
- persist `RUNNING` before invoking bulk import;
- persist one terminal state afterward;
- use `COMPLETED` when all items succeed or already exist;
- use `PARTIALLY_FAILED` when bulk item failures are reported;
- use `FAILED` when the executor itself raises unexpectedly;
- serialize item results into the existing versioned job payload.

Bulk execution SHALL be represented by a structural application port so tests
and future workers can supply alternative implementations.

PR-045 SHALL not add HTTP endpoints or background execution.

## Consequences

- Every lifecycle transition is durable.
- Application tests require no database or network.
- A crashed external executor leaves the most recently persisted state visible.
- HTTP and worker adapters can be added independently.
