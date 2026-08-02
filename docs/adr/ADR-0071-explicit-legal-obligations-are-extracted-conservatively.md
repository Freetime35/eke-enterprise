# ADR-0071 — Explicit Legal Obligations Are Extracted Conservatively

**Status:** Accepted

PR-076 extracts only explicit positive English obligations from structured
document nodes.

Supported markers are `shall`, `must`, `is required to`, `are required to`,
`has to`, and `have to`. Each obligation preserves its subject, action,
source text, source node, language, and nearest article and paragraph.

Negative forms such as `shall not` and `must not` are intentionally excluded
because they represent prohibitions and belong to a separate capability.

The extractor does not infer implicit duties, resolve pronouns, normalize
legal actors, translate content, or use LLM-based interpretation.
