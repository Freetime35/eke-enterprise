# ADR-0032 — CELEX Standard Form Is Modeled Explicitly

**Status:** Accepted

## Context

EKE Enterprise already stores generic `BusinessIdentifier` values, including
the `CELEX` scheme. EUR-Lex imports require more than a non-empty string: the
application needs normalized CELEX values and access to their structural
components.

A CELEX number is language-independent and usually consists of sector, year,
document type, and document number. EUR-Lex also contains specialized forms,
including consolidated texts, corrigenda, and historical variants.

## Decision

The domain SHALL introduce an immutable `CelexIdentifier` value object for the
standard form:

```text
<sector><four-digit year><one-or-two-letter type><four-digit number>
```

Examples:

```text
32023R1114
52016DC0205
61992CJ0396
```

Parsing SHALL:

- trim surrounding whitespace;
- accept an optional `CELEX:` prefix;
- normalize letters to uppercase;
- expose sector, year, document type, and document number;
- convert explicitly to `BusinessIdentifier(CELEX, value)`.

Specialized CELEX variants SHALL not be accepted silently. They require future
explicit models or parser extensions.

## Consequences

- Common CELEX identifiers are normalized before EUR-Lex ingestion.
- Generic identifier handling remains backward compatible.
- Existing API payloads are not globally restricted.
- Unsupported CELEX variants fail clearly instead of being misparsed.
