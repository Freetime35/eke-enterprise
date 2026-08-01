# ADR-0041 — Import Job API Exposes Explicit Synchronous Execution

**Status:** Accepted

## Context

PR-044 introduced persistent import jobs. PR-045 introduced application-level
creation, lookup, and execution. HTTP clients now need access to those
capabilities without introducing background execution prematurely.

## Decision

The presentation layer SHALL expose:

```text
POST /imports/eurlex/jobs
GET  /imports/eurlex/jobs/{job_uuid}
POST /imports/eurlex/jobs/{job_uuid}/run
```

Job creation SHALL return `201 Created` and a `Location` header.

Job execution SHALL remain synchronous and explicit. It SHALL return the
terminal job representation produced by `EurLexImportJobService`.

The API SHALL map:

- malformed CELEX values to `422`;
- missing jobs to `404`;
- invalid lifecycle transitions to `409`.

PR-046 SHALL not add scheduling, retries, background tasks, or workers.

## Consequences

- The complete job lifecycle is accessible over HTTP.
- Application lifecycle rules remain centralized in the service.
- API tests use dependency overrides and require no EUR-Lex network access.
- A future worker can call the same application service.
