# ADR-0005 — Resource Title as a Temporal Localized Concept

**Status:** Accepted

## Context

Legal resources may have titles in multiple languages and may change
title over time.

A raw string is insufficient because it does not express language or
temporal validity.

## Decision

The domain model SHALL represent resource titles through the immutable
`ResourceTitle` business concept.

`ResourceTitle` SHALL contain:

- one `LocalizedText`;
- one `ValidityPeriod`.

The default validity period SHALL be fully open.

`ResourceTitle` SHALL expose behavior for:

- retrieving language and text value;
- checking validity on a date;
- checking language;
- detecting temporal overlap for titles in the same language.

Titles in different languages SHALL not be considered overlapping from
the domain perspective.

## Consequences

### Positive

- Title language is always explicit.
- Historical titles can be represented.
- Overlapping titles in the same language can be detected.
- Source text remains preserved through `LocalizedText`.

### Negative

- The current aggregate does not yet enforce title uniqueness.
- A future `Resource` enrichment will be required to own and validate
  collections of titles.

## Alternatives considered

### Store titles as plain strings

Rejected because language and temporal validity would be lost.

### Store language and validity directly on Resource

Rejected because title-specific behavior would be duplicated and the
aggregate would become less cohesive.
