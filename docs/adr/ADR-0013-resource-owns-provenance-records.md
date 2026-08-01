# ADR-0013 — Resource Owns Provenance Records

**Status:** Accepted

## Context

`ProvenanceRecord` provides immutable source and acquisition evidence for
canonical resource data.

The aggregate requires a clear ownership rule and query behavior so that
provenance cannot be attached to the wrong resource.

## Decision

`Resource` SHALL own an immutable tuple of `ProvenanceRecord` values.

The aggregate SHALL:

- reject non-provenance members;
- reject exact duplicate provenance records;
- require every record to belong to the aggregate ResourceUUID;
- expose queries by source and acquisition method;
- expose inclusive acquisition datetime range filtering;
- expose the most recently acquired provenance record.

Multiple distinct records with the same source reference SHALL be allowed
when acquisition time, method, or checksum differs.

## Consequences

### Positive

- Provenance ownership is centralized.
- Cross-resource provenance mistakes are rejected.
- Repeated acquisitions can be preserved as independent evidence.
- Source and acquisition queries remain domain-native.
- The latest acquisition can be identified without infrastructure logic.

### Negative

- Large provenance histories may require pagination later.
- Exact duplicate detection does not collapse semantically equivalent
  records.
- Version-level or field-level provenance is not yet represented.

## Alternatives considered

### Store only the latest provenance record

Rejected because historical acquisitions and integrity evidence would be
lost.

### Store provenance outside Resource

Rejected because resource ownership could not be enforced by the aggregate.

### Reject repeated source references

Rejected because the same source object may be acquired multiple times.
