# ADR-0065 — Consolidated Acts and Version Lineage Are Explicit

**Status:** Accepted

Standard CELEX identifiers and consolidated-version identifiers are distinct
domain concepts.

Legislative acts continue to use `CelexIdentifier`. Dated consolidated
versions use `EurLexVersionIdentifier`, for example
`02013R0575-20240101`.

A consolidated lineage entry must identify its version, base act and
consolidation date. The date embedded in the version identifier and any
explicit RDF consolidation date must agree.

Initial, codified, recast and corrigendum entries continue to identify
standard legal acts. The importer does not infer applicable versions or
resolve lineage over the network.
