# ADR-0074 — Internal References Are Explicit and Conservatively Resolved

**Status:** Accepted

PR-079 extracts explicit English references to provisions within the same
structured document.

References preserve their source node, source text, reference text, target
ordinal, language, and nearest article and paragraph. A target node is set
only when exactly one node of the expected kind has a matching ordinal.

Ranges, missing targets, and ambiguous matches remain unresolved. The
extractor does not resolve references to external acts, pronouns such as
`that Article`, relative expressions such as `the previous paragraph`, or
references in languages other than English.
