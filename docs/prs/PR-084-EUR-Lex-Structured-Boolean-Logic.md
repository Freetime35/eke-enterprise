# PR-084 — EUR-Lex Structured Boolean Logic

Adds:

- immutable Boolean atoms and operation nodes;
- closed acyclic expression trees;
- `NOT`, `AND` and `OR` operators;
- precedence-aware recursive parsing;
- nested parenthesis support;
- immutable tokenization;
- conservative linguistic-negation handling;
- deterministic expression identifiers;
- source-qualifier linkage;
- application tests;
- ADR-0079.

No Boolean simplification, executable evaluation engine, persistence
migration or public HTTP endpoint change is required.
