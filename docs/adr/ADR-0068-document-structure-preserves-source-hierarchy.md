# ADR-0068 — Document Structure Preserves Source Hierarchy

**Status:** Accepted

Structured EUR-Lex XML or XHTML is parsed separately from RDF/XML metadata.

Each recognized structural element becomes an immutable node with a stable
identifier, source position, source element and explicit parent identifier.
Document order and hierarchy are preserved without interpreting legal meaning.

Tables, formulas, footnotes and visual elements are retained as structural
nodes and referenced from their parent through `embedded_content_ids`. Their
internal semantics remain outside PR-073.

The parser does not infer missing headings, translate content, perform OCR, or
extract obligations and definitions.
