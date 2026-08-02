# PR-076 — EUR-Lex Legal Obligations Extraction

Adds:

- immutable explicit legal-obligation values;
- positive English obligation extraction;
- support for `shall`, `must`, `required to`, and `has to`;
- subject and article-scoped lookup;
- deterministic deduplication;
- source-node, article and paragraph provenance;
- deliberate exclusion of prohibitions;
- a parser operating on PR-073 document structures;
- application and infrastructure tests;
- ADR-0071.

No persistence migration or public HTTP endpoint change is required.
