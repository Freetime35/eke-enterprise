# ADR-0009 — Resource Version Has Dedicated Internal Identity

**Status:** Accepted

## Context

A canonical resource may exist through multiple historical, consolidated,
corrected, or source-derived versions.

The resource identity must remain stable while each individual version
also needs a durable internal identity for persistence, provenance,
relationships, and synchronization.

## Decision

The domain model SHALL identify every resource version through a dedicated
`ResourceVersionUUID`.

`ResourceVersion` SHALL contain:

- one `ResourceVersionUUID`;
- one owning `ResourceUUID`;
- one `ResourceStatus`;
- one `ValidityPeriod`;
- an optional previous `ResourceVersionUUID`.

A version SHALL NOT reference itself as its previous version.

Direct succession SHALL require:

- both versions to belong to the same resource;
- the newer version to reference the older version identity.

## Consequences

### Positive

- Resource identity and version identity remain distinct.
- Versions can be persisted and referenced independently.
- Direct predecessor chains can be represented.
- Version behavior remains infrastructure-independent.

### Negative

- Version sequence numbers and source labels are not yet modeled.
- Branching version histories are possible and require later policies.
- Provenance and manifestation linkage remain future concepts.

## Alternatives considered

### Reuse ResourceUUID for versions

Rejected because the resource and its versions are different identity
scopes.

### Use integer sequence numbers as identity

Rejected because numbers are not globally unique and may differ by source.

### Use source version labels as identity

Rejected because source labels may be absent, unstable, or non-unique.
