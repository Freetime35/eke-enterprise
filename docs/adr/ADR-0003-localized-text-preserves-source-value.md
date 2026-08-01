# ADR-0003 — Localized Text Preserves Source Value

**Status:** Accepted

## Context

Legal titles, summaries, labels, and other textual metadata are
language-dependent.

Source systems may provide meaningful leading or trailing whitespace,
punctuation, capitalization, or formatting differences. Automatic
normalization could alter evidentiary source values.

## Decision

The domain model SHALL represent language-dependent text through the
immutable `LocalizedText` value object.

`LocalizedText` SHALL:

- contain one `LanguageCode`;
- contain one non-empty string value;
- reject empty and whitespace-only values;
- preserve the original text exactly as provided;
- remain independent of source systems and persistence technologies.

Text normalization, whitespace cleanup, Unicode normalization, and
source-specific transformations SHALL occur outside this value object.

## Consequences

### Positive

- Source text remains reproducible and traceable.
- Language is always explicit.
- Equality and hashing remain deterministic.
- Infrastructure-specific cleanup does not leak into the domain model.

### Negative

- Semantically equivalent text with different whitespace remains unequal.
- Consumers requiring normalized search values must derive them separately.

## Alternatives considered

### Strip surrounding whitespace automatically

Rejected because it would modify the source value.

### Store language and text as separate primitive fields

Rejected because it would weaken the invariant that localized text always
carries an explicit language.
