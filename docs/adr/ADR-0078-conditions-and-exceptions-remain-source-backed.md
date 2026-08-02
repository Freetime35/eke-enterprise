# ADR-0078 — Conditions and Exceptions Remain Source-Backed

**Status:** Accepted

PR-083 extracts only explicit leading or trailing rule qualifiers introduced
by a fixed marker set such as `if`, `where`, `provided that`, `unless` and
`except where`.

Qualifiers retain the originating rule, requirement, node, source text and
already-resolved reference identifiers. Identifiers are deterministic.

The extractor does not parse nested conditions, normalize Boolean logic,
infer implicit exceptions, structure thresholds, resolve pronouns, translate
clauses or use probabilistic NLP or LLM inference.
