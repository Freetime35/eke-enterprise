# ADR-0014 — Classification Concepts Preserve Scheme Codes

**Status:** Accepted

## Context

Legal resources may be classified through EuroVoc, directory codes,
subject-matter taxonomies, policy areas, and internal schemes.

Classification codes are meaningful within their owning scheme and may
include formatting that must remain reproducible.

## Decision

The domain model SHALL represent classification entries through the
immutable `ClassificationConcept` value object.

Every concept SHALL contain:

- one canonical `ClassificationScheme`;
- one non-empty code;
- one `LocalizedText` label;
- one `ValidityPeriod`.

Codes and labels SHALL be preserved exactly as supplied.

Code normalization and source-specific mapping SHALL occur outside the
value object.

## Consequences

### Positive

- Scheme and code are always coupled.
- Labels are explicitly localized.
- Historical taxonomy concepts can be represented.
- Source codes remain reproducible.
- The model remains independent of taxonomy APIs and persistence.

### Negative

- Equivalent formatting variants remain unequal.
- Code uniqueness within a scheme is not enforced globally.
- Hierarchical parent-child relationships are not yet modeled.

## Alternatives considered

### Use free-form taxonomy names

Rejected because spelling and semantics would be uncontrolled.

### Normalize classification codes automatically

Rejected because formatting may be scheme-specific and evidentiary.

### Store labels without language

Rejected because classification labels are multilingual.
