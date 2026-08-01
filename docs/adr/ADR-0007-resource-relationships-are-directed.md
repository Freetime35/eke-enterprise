# ADR-0007 — Resource Relationships Are Directed

**Status:** Accepted

## Context

Legal and regulatory resources form a graph of citations, amendments,
repeals, consolidations, implementations, transpositions, corrections,
and other links.

Most of these relationships have an explicit direction. For example, one
resource amends another resource, while the inverse statement is that the
second resource is amended by the first.

## Decision

The canonical domain model SHALL represent inter-resource links through
the immutable `ResourceRelationship` business concept.

Every relationship SHALL contain:

- one source `ResourceUUID`;
- one target `ResourceUUID`;
- one canonical `RelationshipType`;
- one `ValidityPeriod`.

Source and target SHALL identify different resources.

Relationships SHALL be directed. Inverse relationship types may be
represented explicitly when required by ingestion or query use cases.

## Consequences

### Positive

- Graph direction is explicit.
- Relationship validity can be modeled over time.
- Connectors can map source-specific relation types into one vocabulary.
- The concept is independent of Neo4j, RDF, or relational persistence.

### Negative

- Inverse relationships may produce duplicate graph facts if both are
  stored.
- Relationship provenance is not yet represented.
- Self-referential relationships are prohibited in the initial model.

## Alternatives considered

### Store undirected resource pairs

Rejected because amendment, repeal, implementation, and legal-basis
relations are directional.

### Use source-specific relationship labels

Rejected because the canonical domain must remain source-independent.

### Store relationships directly as Neo4j edges

Rejected because the domain model must not depend on graph persistence.
