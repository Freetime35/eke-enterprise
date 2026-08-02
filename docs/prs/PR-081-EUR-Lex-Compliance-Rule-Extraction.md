# PR-081 — EUR-Lex Compliance Rule Extraction

Adds:

- immutable compliance-rule values;
- requirement, permission and prohibition rule kinds;
- deterministic one-rule-per-requirement extraction;
- retained source requirement, node, text and language provenance;
- resolved document-reference and definition identifiers;
- subject, article and kind query helpers;
- deterministic rule identifiers;
- application tests;
- ADR-0076.

No persistence migration, executable policy engine or public HTTP endpoint
change is required.
