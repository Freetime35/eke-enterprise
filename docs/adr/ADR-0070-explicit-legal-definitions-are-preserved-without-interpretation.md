# ADR-0070 — Explicit Legal Definitions Are Preserved Without Interpretation

**Status:** Accepted

PR-075 extracts only explicit English legal definitions from structured
document nodes.

Recognized formulations include `means`, `shall mean`,
`is to be understood as`, and `has the meaning`. Definitions retain the
original source text, source node, language, and nearest article and paragraph
identifiers.

The extractor does not infer synonyms, resolve external definitions, translate
terms, use embeddings, or apply LLM-based interpretation. Non-English content
is ignored.
