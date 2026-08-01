# ADR-0010 — Resource Owns Canonical Titles and Versions

**Status:** Accepted

## Context

The initial `Resource` aggregate represented internal identity and
external business identifiers.

The canonical model now includes localized temporal titles, lifecycle
status, resource type, and independently identified resource versions.

Aggregate-level invariants are required to prevent inconsistent title
histories and versions belonging to another resource.

## Decision

`Resource` SHALL own:

- one `ResourceType`;
- one `ResourceStatus`;
- zero or more `ResourceTitle` values;
- zero or more `ResourceVersion` values.

Defaults SHALL preserve compatibility with minimal construction:

- `ResourceType.OTHER`;
- `ResourceStatus.UNKNOWN`;
- empty title collection;
- empty version collection.

The aggregate SHALL enforce:

- unique titles;
- no overlapping title validity periods in the same language;
- unique resource version identities;
- every version belongs to the aggregate resource;
- every referenced previous version exists in the aggregate.

The aggregate SHALL expose title and version query behavior instead of
requiring consumers to inspect collections manually.

## Consequences

### Positive

- Canonical title and version consistency is centralized.
- Existing minimal Resource construction remains valid.
- Query behavior is expressed through the domain language.
- Persistence and API layers inherit stable aggregate invariants.

### Negative

- The immutable aggregate requires replacement when collections change.
- Branched version histories remain possible.
- Aggregate status and version statuses are not yet cross-validated.
- Large title or version collections may require future performance work.

## Alternatives considered

### Keep titles and versions outside Resource

Rejected because ownership and consistency rules would be fragmented.

### Require type and status without defaults

Rejected because it would break the existing public constructor and make
incremental ingestion harder.

### Permit overlapping same-language titles

Rejected because a date-specific title lookup would become ambiguous.
