# ADR-0001 — Resource as the Primary Aggregate Root

**Status:** Accepted

## Context

EKE Enterprise must represent resources originating from multiple
authoritative legal and regulatory source systems.

External identifiers such as CELEX, ELI, CELLAR, and ECLI are not
sufficient as internal identities because they belong to external
authorities and may not exist for every future source.

## Decision

The canonical domain model SHALL use `Resource` as its primary aggregate
root.

Every `Resource` SHALL own:

- exactly one immutable `ResourceUUID`;
- at least one external `BusinessIdentifier`;
- no duplicate business identifier;
- at most one identifier for each `IdentifierScheme`.

Consumers SHALL use aggregate behavior such as `has_identifier`,
`find_identifier`, and `has_identifier_scheme` instead of implementing
identifier lookup logic outside the aggregate.

## Consequences

### Positive

- Internal identity remains independent of source systems.
- Identifier lookup behavior is centralized.
- Aggregate invariants are enforced at construction time.
- Future source connectors can converge on one canonical resource model.

### Negative

- The initial model does not support multiple identifiers under the same
  scheme.
- Adding identifier history or aliases will require a future domain
  decision.

## Alternatives considered

### Use CELEX as the internal primary key

Rejected because EKE Enterprise is designed to support non-EUR-Lex
sources.

### Store identifiers as an unvalidated collection

Rejected because duplicate or ambiguous identifier schemes would weaken
canonical identity guarantees.
