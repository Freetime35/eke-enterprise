# ADR-0002 — Canonical Language Code Representation

**Status:** Accepted

## Context

EKE Enterprise initially processes English-language resources but must
remain compatible with multilingual legal sources.

Source systems may expose language identifiers using different casing,
for example `EN`, `en`, or values surrounded by whitespace.

## Decision

The domain model SHALL represent language identifiers through the
immutable `LanguageCode` value object.

`LanguageCode` SHALL:

- accept exactly two ASCII alphabetic characters;
- normalize values to lowercase;
- expose uppercase conversion for source-system interoperability;
- remain independent of external language registries and libraries.

The first implementation validates ISO 639-1 syntax only. It does not
verify membership in the complete ISO 639-1 registry.

## Consequences

### Positive

- Language values have one canonical representation.
- Equality and hashing are case-insensitive through normalization.
- The domain remains dependency-free.
- Future multilingual value objects can reuse `LanguageCode`.

### Negative

- Syntactically valid but unassigned two-letter codes are accepted.
- BCP 47 language tags are not supported in this version.

## Alternatives considered

### Use an enumeration containing all supported languages

Rejected because it would require maintaining a language registry in the
domain and would make extension less flexible.

### Store raw strings

Rejected because casing and whitespace differences would produce
inconsistent canonical values.
