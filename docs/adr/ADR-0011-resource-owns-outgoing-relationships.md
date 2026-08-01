# ADR-0011 — Resource Owns Outgoing Relationships

**Status:** Accepted

## Context

The canonical domain model already represents directed
`ResourceRelationship` values.

The `Resource` aggregate requires a clear ownership rule so that
relationship collections can be validated consistently without loading
other aggregates.

## Decision

`Resource` SHALL own only relationships whose source identity equals the
aggregate `ResourceUUID`.

The aggregate SHALL:

- store relationships as an immutable tuple;
- reject non-relationship members;
- reject exact duplicate relationships;
- reject relationships that do not originate from the aggregate;
- expose queries by relationship type, target resource, and active date.

Incoming relationships SHALL be queried through repositories or graph
services rather than stored in the target aggregate.

Distinct relationship types between the same source and target SHALL be
allowed.

## Consequences

### Positive

- Relationship ownership is explicit.
- Aggregate validation does not require loading target resources.
- Directional graph semantics remain clear.
- Outgoing relationship queries are domain-native.
- Persistence models can map aggregate-owned edges consistently.

### Negative

- Incoming relationship queries require an external query mechanism.
- Large outgoing relationship collections may require pagination later.
- Exact duplicate detection does not collapse semantically equivalent
  inverse relations.

## Alternatives considered

### Store both outgoing and incoming relationships

Rejected because it would duplicate graph facts and create cross-aggregate
synchronization problems.

### Store relationships outside Resource only

Rejected because the aggregate would not enforce ownership or duplicate
invariants.

### Reject multiple relationship types to the same target

Rejected because one resource may both cite and amend another resource.
