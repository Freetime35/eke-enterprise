# ADR-0072 — Explicit Legal Permissions Are Extracted Conservatively

**Status:** Accepted

PR-077 extracts only explicit positive English permissions from structured
document nodes.

Supported markers are `may`, `is entitled to`, `are entitled to`,
`is authorised to`, `are authorised to`, `is allowed to`, and
`are allowed to`. Each permission preserves its subject, action, source
text, source node, language, and nearest article and paragraph.

Negative forms such as `may not`, `is not authorised to`, and
`is not allowed to` are intentionally excluded because they represent
prohibitions and belong to a separate capability.

The extractor does not infer implicit rights, distinguish factual
possibility from legal permission beyond explicit patterns, resolve
pronouns, translate content, or use LLM-based interpretation.
