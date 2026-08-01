# ADR-0036 — EUR-Lex Import Is Exposed as an Idempotent Command

**Status:** Accepted

## Context

The application layer can now retrieve, parse, map, and atomically persist one
EUR-Lex Resource by CELEX identifier. External clients need a stable HTTP entry
point without gaining access to transport, parsing, or persistence details.

## Decision

The presentation layer SHALL expose:

```text
POST /imports/eurlex
```

with a request containing one CELEX identifier.

The endpoint SHALL:

- parse and normalize the CELEX value;
- delegate exclusively to `EurLexResourceImportService`;
- return `201 Created` when a new Resource is persisted;
- return `200 OK` when the CELEX already exists;
- return a `Location` header pointing to the canonical Resource;
- return the standard Resource representation;
- map an absent upstream document to `404`;
- map upstream and metadata failures to `502`;
- reject malformed CELEX input with `422`.

The composition root SHALL create one shared `HttpxEurLexClient` for the
application lifespan and close it during shutdown.

## Consequences

- EUR-Lex import is available to HTTP clients.
- Idempotence remains defined by the application service.
- Presentation code contains no retrieval or mapping logic.
- HTTP resources are cleaned up predictably.
- OpenAPI path, tag, operation ID, and error responses are contract-tested.
