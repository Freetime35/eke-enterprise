# ADR-0024 — Resource HTTP API Exposes Stable Core Fields

**Status:** Accepted

## Context

Resource is a rich aggregate containing titles, versions, relationships,
provenance records, and classifications. Exposing the complete aggregate
in the first HTTP API would create a large and unstable external contract.

## Decision

The first Resource CRUD API SHALL expose only:

- internal Resource UUID;
- business identifiers;
- ResourceType;
- ResourceStatus.

Create operations SHALL initialize richer collections as empty.

Update operations SHALL preserve existing rich collections while
replacing only the HTTP-editable core fields.

Application exceptions SHALL map to stable HTTP error codes:

- ResourceNotFoundError → 404;
- ResourceAlreadyExistsError → 409.

## Consequences

- The initial HTTP contract remains small and stable.
- Existing rich aggregate data cannot be lost through core-field updates.
- Rich subresources can be introduced incrementally in later PRs.
- API consumers cannot yet manage titles, versions, relationships,
  provenance, or classifications.
