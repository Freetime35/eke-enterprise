# ADR-0069 — Complex Content Is Preserved Before Interpretation

**Status:** Accepted

Tables, formulas, footnotes and visual elements are parsed separately from
document hierarchy and preserved without semantic interpretation.

Table geometry, MathML, text, media URIs, note markers and source positions
are retained when explicitly present. No OCR, image analysis, formula
evaluation or regulatory interpretation is performed.

Complex content items retain their source identifiers when available and
otherwise receive deterministic identifiers. Each item records its parent
structural node.
