# PR-063 — EUR-Lex Relationships Import

Adds:

- CDM predicate mapping to canonical relationship types;
- RDF/XML extraction of directed CELEX relationships;
- deterministic relation deduplication;
- import of relationships only for already resolved targets;
- prevention of incomplete placeholder Resource creation;
- application and infrastructure tests;
- ADR-0058.

No migration or public HTTP endpoint change is required.
