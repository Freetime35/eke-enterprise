# ADR-0081 — Quantitative Thresholds Preserve Explicit Values and Units

**Status:** Accepted

## Decision

Represent only explicit quantitative thresholds appearing in EUR-Lex text.

The model preserves:

- comparator;
- numeric value;
- optional upper bound;
- explicit unit;
- explicit currency;
- complete provenance.

No conversions or inferred values are performed.

## Consequences

Downstream services may perform calculations later while the extracted model
remains source-backed and deterministic.
