# ADR-0075 — Requirements Graph Contains Only Source-Backed Links

**Status:** Accepted

PR-080 assembles previously extracted obligations, permissions,
prohibitions, definitions and internal references into a deterministic
closed graph.

Graph identifiers use stable SHA-256-derived values rather than Python's
process-dependent `hash()`. Links are created only from explicit source
provenance or exact normalized subject equality.

Unresolved internal references produce no graph edge. Subject-definition
and same-subject links use exact case-insensitive matching only. No
synonymy, lemmatization, pronoun resolution, confidence scoring or
LLM-based inference is performed.
