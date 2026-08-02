# PR-073 — EUR-Lex Document Structure Extraction

Adds:

- immutable document nodes and ordered document structures;
- preamble, recital, part, title, chapter, section, article, paragraph, point,
  annex and appendix support;
- preserved table, formula, footnote and visual placeholders;
- deterministic identifiers when the source has no identifier;
- explicit parent-child hierarchy;
- a dedicated XML/XHTML structure parser separated from RDF metadata parsing;
- application and infrastructure tests;
- ADR-0068.

No persistence migration or public HTTP endpoint change is required.
