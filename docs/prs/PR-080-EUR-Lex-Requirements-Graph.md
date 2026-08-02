# PR-080 — EUR-Lex Requirements Graph

Adds:

- requirement nodes for obligations, permissions and prohibitions;
- definition nodes and lightweight document nodes;
- `LOCATED_IN`, `REFERENCES`, `DEFINES_SUBJECT` and `SAME_SUBJECT` edges;
- deterministic graph and edge identifiers;
- closed-graph validation;
- source-backed graph construction from PR-075 through PR-079 outputs;
- graph query helpers;
- application tests;
- ADR-0075.

No persistence migration or public HTTP endpoint change is required.
