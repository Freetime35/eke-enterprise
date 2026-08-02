# PR-078 — EUR-Lex Legal Prohibitions Extraction

Adds:

- immutable explicit legal-prohibition values;
- English prohibition extraction;
- support for `shall not`, `must not`, `may not`, `prohibited from`,
  `not authorised to`, and `not allowed to`;
- subject and article-scoped lookup;
- deterministic deduplication;
- source-node, article and paragraph provenance;
- a parser operating on PR-073 document structures;
- application and infrastructure tests;
- ADR-0073.

No persistence migration or public HTTP endpoint change is required.
