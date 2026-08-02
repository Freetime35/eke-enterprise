# PR-083 — EUR-Lex Conditions and Exceptions

Adds:

- immutable rule-condition and rule-exception values;
- explicit qualifier markers;
- conservative leading and trailing qualifier extraction;
- deterministic qualifier identifiers;
- retained rule, requirement, node and source-text provenance;
- propagation of already-resolved internal reference identifiers;
- rule, kind, condition and exception query helpers;
- application tests;
- ADR-0078.

No Boolean expression model, persistence migration, XML parsing change or
public HTTP endpoint change is required.
