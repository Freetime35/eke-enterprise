# ADR-0004 — Validity Period Uses Inclusive Boundaries

**Status:** Accepted

## Context

Legal and regulatory facts may be valid during a bounded period, from an
unknown start, until an unknown end, or without either boundary.

The domain needs one canonical temporal interval representation for
versions, titles, relationships, classifications, and future legal
effects.

## Decision

The domain model SHALL represent date-level temporal validity through the
immutable `ValidityPeriod` value object.

`ValidityPeriod` SHALL:

- use `datetime.date` boundaries;
- allow an open start through `valid_from=None`;
- allow an open end through `valid_to=None`;
- allow both boundaries to be open;
- treat both boundaries as inclusive;
- reject a start date later than the end date;
- provide date containment and interval overlap behavior.

Periods touching at one boundary date SHALL overlap.

## Consequences

### Positive

- Temporal rules are centralized in one value object.
- Open-ended legal validity is represented explicitly.
- Equality and hashing are deterministic.
- Inclusive legal dates are easy to reason about.

### Negative

- Time-of-day precision is not supported.
- Alternative interval semantics require a future domain decision.
- Fully open periods are allowed and must be interpreted carefully by
  consumers.

## Alternatives considered

### Use `datetime.datetime`

Rejected because the initial legal validity use cases are date-based and
do not require time-of-day precision.

### Use exclusive upper boundaries

Rejected because published legal validity dates are more naturally
interpreted as inclusive in the initial domain scope.

### Store primitive start and end fields on each entity

Rejected because temporal validation and behavior would be duplicated
across the domain.
