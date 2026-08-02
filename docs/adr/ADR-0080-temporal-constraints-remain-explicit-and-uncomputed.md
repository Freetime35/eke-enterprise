# ADR-0080 — Temporal Constraints Remain Explicit and Uncomputed

**Status:** Accepted

## Context

Compliance rules frequently contain deadlines, durations, recurrence
requirements and temporal anchors. These expressions are legally relevant,
but calculating operational due dates requires information that may not be
present in the source document.

Examples include:

- `within 30 days of notification`;
- `no later than 15 March 2027`;
- `for a period of five years`;
- `every six months`;
- `annually`.

## Decision

Temporal constraints are represented as immutable, source-backed values.

The representation preserves:

- the temporal kind;
- the explicit relation;
- the matched source text;
- an absolute date when explicitly stated;
- a positive quantity and unit when explicitly stated;
- an unresolved anchor label when explicitly stated;
- complete rule, requirement, node and qualifier provenance.

Constraint identifiers are deterministic and use SHA-256-derived values.

The extractor operates only on existing compliance-rule and qualifier text.
It does not revisit XML and does not introduce temporal facts absent from
the source.

## Consequences

The model can represent deadlines and recurrence without pretending that an
operational due date has been computed.

Downstream services may later combine these values with resolved events,
calendars and jurisdiction-specific rules, but those calculations remain
outside PR-085.

## Rejected alternatives

### Compute deadlines immediately

Rejected because event dates, business-day conventions, holidays, time
zones, suspension rules and extensions may be unavailable.

### Store temporal expressions as untyped strings only

Rejected because explicit dates, quantities, units and relations can be
represented deterministically without legal interpretation.

### Infer implicit temporal constraints

Rejected because it would weaken source traceability and introduce
unsupported interpretation.
