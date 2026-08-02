# ADR-0066 — Corrigenda Have Dedicated Identifiers

**Status:** Accepted

EUR-Lex corrigenda such as `32013L0036R(01)` are not parsed as standard
CELEX identifiers and are not treated as consolidated versions.

`EurLexCorrigendumIdentifier` stores the standard base-act CELEX identifier
and a strictly positive corrigendum sequence. Its canonical value always
uses the `R(01)` form.

Corrigendum metadata remains source-backed. Publication dates are optional
and stored only when explicitly present in RDF/XML. The importer does not
infer correction dates or resolve corrigenda over the network.
