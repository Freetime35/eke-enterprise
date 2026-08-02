# PR-077 — EUR-Lex Legal Permissions Extraction

Adds:

- immutable explicit legal-permission values;
- positive English permission extraction;
- support for `may`, `entitled to`, `authorised to`, and `allowed to`;
- subject and article-scoped lookup;
- deterministic deduplication;
- source-node, article and paragraph provenance;
- deliberate exclusion of negative permissions;
- a parser operating on PR-073 document structures;
- application and infrastructure tests;
- ADR-0072.

No persistence migration or public HTTP endpoint change is required.
