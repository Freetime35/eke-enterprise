# ADR-0008 — Resource Status as a Controlled Lifecycle Vocabulary

**Status:** Accepted

## Context

Authoritative legal and regulatory sources expose lifecycle information
using heterogeneous labels and sometimes incomplete semantics.

The canonical domain model requires one stable vocabulary for describing
whether a resource is in preparation, adopted, published, effective, or
no longer legally active.

## Decision

The domain model SHALL represent lifecycle state through the
`ResourceStatus` string enumeration.

The initial vocabulary SHALL include:

- DRAFT
- ADOPTED
- PUBLISHED
- IN_FORCE
- PARTIALLY_IN_FORCE
- NOT_YET_IN_FORCE
- REPEALED
- EXPIRED
- WITHDRAWN
- ANNULLED
- SUPERSEDED
- UNKNOWN

`ResourceStatus` SHALL expose behavior for determining whether a status:

- is terminal;
- is effective;
- is pre-effective.

Source connectors SHALL map source-specific status labels to this
canonical vocabulary.

## Consequences

### Positive

- Lifecycle state is strongly typed.
- Source-specific labels remain outside the domain model.
- Consumers can query semantic groups without duplicating logic.
- Serialization remains stable and straightforward.

### Negative

- Some legal systems may require more detailed lifecycle states.
- `UNKNOWN` may hide source-quality problems if used excessively.
- Future transition rules will require an additional domain concept.

## Alternatives considered

### Store free-form lifecycle strings

Rejected because they would create inconsistent semantics and spelling.

### Derive lifecycle only from dates

Rejected because legal effect cannot always be inferred from dates alone.

### Encode status only as booleans

Rejected because multiple lifecycle dimensions cannot be represented
accurately through a small set of flags.
