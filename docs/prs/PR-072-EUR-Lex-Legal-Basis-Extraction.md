# PR-072 — EUR-Lex Legal Basis Extraction

Adds:

- canonical legal-basis kinds;
- explicit URI and CELEX targets;
- optional treaty, article, paragraph and source label fields;
- separation from generic references introduced in PR-069;
- deterministic deduplication;
- `EurLexMetadata` and RDF/XML parser integration;
- application and infrastructure tests;
- ADR-0067.

No migration or public HTTP endpoint change is required.
