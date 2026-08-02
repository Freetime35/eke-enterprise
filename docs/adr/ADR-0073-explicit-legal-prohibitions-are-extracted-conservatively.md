# ADR-0073 — Explicit Legal Prohibitions Are Extracted Conservatively

**Status:** Accepted

PR-078 extracts only explicit English prohibitions from structured document
nodes.

Supported markers are `shall not`, `must not`, `may not`,
`is prohibited from`, `are prohibited from`, `is not authorised to`,
`are not authorised to`, `is not allowed to`, and `are not allowed to`.

Each prohibition preserves its subject, action, source text, source node,
language, and nearest article and paragraph.

The extractor does not infer implicit prohibitions, resolve pronouns,
translate content, reinterpret positive obligations or permissions, or use
LLM-based interpretation.
