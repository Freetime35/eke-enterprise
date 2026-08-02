# PR-082 — EUR-Lex Regulated Actors and Legal Subjects

Adds:

- immutable legal actor and actor-mention values;
- deterministic actor and mention identifiers;
- exact normalized actor reuse across requirements;
- conservative explicit actor classification;
- regulated-entity classification when one exact definition is linked;
- actor, kind, mention and requirement query helpers;
- validation that mentions target existing actors;
- application tests;
- ADR-0077.

No graph schema change, persistence migration, pronoun resolution,
coordinated-subject parsing or public HTTP endpoint change is required.
