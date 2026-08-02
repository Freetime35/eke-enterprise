# PR-079 — EUR-Lex Cross References and Internal References

Adds:

- immutable explicit internal-reference values;
- article, paragraph, point, chapter, section, part, title, annex and
  appendix reference kinds;
- English reference extraction;
- conservative target resolution using structure kind and ordinal;
- unresolved reference inspection;
- source-node, article and paragraph provenance;
- deterministic deduplication;
- application and infrastructure tests;
- ADR-0074.

External-act references remain covered by PR-069. No persistence migration
or public HTTP endpoint change is required.
