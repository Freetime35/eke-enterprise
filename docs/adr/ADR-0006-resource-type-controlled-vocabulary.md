# ADR-0006 — Resource Type as a Controlled Vocabulary

**Status:** Accepted

## Context

Authoritative legal and regulatory sources classify resources using
source-specific vocabularies.

EUR-Lex, CELLAR, ELI, supervisory authorities, and future connectors may
use different labels for equivalent legal or documentary categories.

The canonical domain model requires one stable, source-independent
vocabulary.

## Decision

The domain model SHALL represent the canonical resource classification
through the `ResourceType` string enumeration.

The initial vocabulary SHALL include:

- REGULATION
- DIRECTIVE
- DECISION
- RECOMMENDATION
- OPINION
- TREATY
- CASE_LAW
- NOTICE
- COMMUNICATION
- GUIDELINE
- REPORT
- PROPOSAL
- CORRIGENDUM
- OTHER

Source connectors SHALL map source-specific classifications to this
canonical vocabulary.

`OTHER` SHALL be used only when a resource cannot be mapped to a more
precise canonical type.

## Consequences

### Positive

- Resource types are stable and strongly typed.
- Source-specific taxonomies remain outside the domain model.
- Serialization is straightforward.
- Future APIs and persistence layers share one vocabulary.

### Negative

- The initial vocabulary may not cover every future source category.
- Mapping rules will be required in source connectors.
- Adding a new canonical type requires a deliberate domain change.

## Alternatives considered

### Store source labels directly

Rejected because source labels are not stable or interoperable.

### Use free-form strings

Rejected because they would allow spelling differences and uncontrolled
vocabulary growth.

### Model every source category in the domain

Rejected because the canonical model must remain source-independent.
