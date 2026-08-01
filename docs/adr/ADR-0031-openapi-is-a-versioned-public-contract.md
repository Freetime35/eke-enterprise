# ADR-0031 — OpenAPI Is a Versioned Public Contract

**Status:** Accepted

## Context

The EKE HTTP API now exposes Resource CRUD, search, titles, versions,
relationships, provenance, and classifications. Client generators and external
integrations need stable operation identifiers, discoverable tag metadata, and
tests that detect accidental path removal or renaming.

## Decision

The OpenAPI document SHALL be treated as a public API contract.

The application SHALL:

- define documented tags for every public route group;
- generate deterministic operation IDs from the first route tag and function
  name;
- publish a stable API description;
- provide reusable application and validation error schemas;
- test the complete set of public paths;
- test operation-ID uniqueness and representative stable identifiers.

The contract tests intentionally fail when a public path is added, removed, or
renamed without updating the expected contract.

## Consequences

- Generated clients receive stable method names.
- Accidental breaking changes are detected during tests.
- New endpoints require explicit contract-test updates.
- OpenAPI evolution becomes a reviewed architectural change.
