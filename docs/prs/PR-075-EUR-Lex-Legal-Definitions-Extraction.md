# PR-075 — EUR-Lex Legal Definitions Extraction

Adds:

- immutable explicit legal-definition values;
- English-only definition extraction;
- normalized term lookup;
- article-scoped definition lookup;
- deterministic deduplication;
- source-node, article and paragraph provenance;
- a parser operating on PR-073 document structures;
- application and infrastructure tests;
- ADR-0070.

No persistence migration or public HTTP endpoint change is required.
