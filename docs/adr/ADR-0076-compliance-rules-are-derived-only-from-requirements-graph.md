# ADR-0076 — Compliance Rules Are Derived Only from Requirements Graph

**Status:** Accepted

PR-081 derives compliance rules exclusively from PR-080 requirements graph
nodes and edges.

One compliance rule is produced for each requirement node. Rule identifiers
use stable SHA-256-derived values based on source requirement identifiers.
Resolved internal references and linked definitions are copied from graph
edges without re-reading or reinterpreting source text.

The extractor does not infer conditions, exceptions, deadlines, sanctions,
evidence requirements, actors, executable checks, confidence scores, or
semantic relationships absent from the graph.
