# ADR-0015 — Resource Owns Classification Concepts

**Status:** Accepted

## Context

`ClassificationConcept` represents a taxonomy assignment through scheme,
code, localized label, and temporal validity.

The `Resource` aggregate requires ownership and uniqueness rules so that
classifications remain queryable and non-ambiguous.

## Decision

`Resource` SHALL own an immutable tuple of `ClassificationConcept`
values.

The aggregate SHALL:

- reject non-classification members;
- reject exact duplicate concepts;
- reject repeated scheme, code, and language combinations;
- allow the same scheme and code in different languages;
- allow the same code in different schemes;
- expose queries by scheme, scheme-plus-code, label language, and date.

## Consequences

### Positive

- Classification ownership is centralized.
- Multilingual labels for one code are supported.
- Scheme boundaries remain explicit.
- Query behavior is domain-native.
- Temporal classifications can be filtered consistently.

### Negative

- The same scheme and code cannot currently have overlapping historical
  labels in one language.
- Hierarchical classification relationships remain future work.
- Large classification sets may require indexed query support later.

## Alternatives considered

### Reject duplicate scheme and code regardless of language

Rejected because canonical concepts may require multilingual labels.

### Permit repeated scheme, code, and language combinations

Rejected because lookup results would become ambiguous.

### Store classification concepts outside Resource

Rejected because ownership and uniqueness would not be enforced by the
aggregate.
