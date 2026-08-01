# ADR-0012 — Provenance Records Are Immutable and Timezone-Aware

**Status:** Accepted

## Context

Canonical resource data must remain traceable to its source, source-side
reference, acquisition method, and acquisition time.

Provenance metadata is evidentiary and must not change after creation.

Acquisition timestamps may originate from systems operating in different
time zones.

## Decision

The domain model SHALL represent acquisition provenance through the
immutable `ProvenanceRecord` business concept.

Every record SHALL contain:

- one `ResourceUUID`;
- one canonical `ProvenanceSource`;
- one non-empty source reference;
- one timezone-aware acquisition datetime;
- one canonical `AcquisitionMethod`;
- an optional non-empty checksum.

The record SHALL preserve source references and checksums exactly as
supplied.

## Consequences

### Positive

- Every record is attributable to a canonical resource and source.
- Acquisition times are unambiguous.
- Checksums can support integrity verification.
- Provenance remains independent of persistence and ingestion frameworks.

### Negative

- Source-specific metadata beyond the reference is not yet modeled.
- Checksum algorithms are not validated in this version.
- Version-level provenance requires a future extension.

## Alternatives considered

### Use naive datetimes

Rejected because acquisition times would be ambiguous across systems.

### Store provenance only in ingestion logs

Rejected because logs are operational artifacts and not durable domain
evidence.

### Normalize source references automatically

Rejected because source-side identifiers and locators must remain
reproducible.
