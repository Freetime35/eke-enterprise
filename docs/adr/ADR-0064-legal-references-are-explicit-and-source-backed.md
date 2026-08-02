# ADR-0064 — Legal References Are Explicit and Source-Backed

**Status:** Accepted

EUR-Lex legal references are represented separately from strong legal
relationships such as amendment, repeal or replacement.

Each reference retains its RDF predicate and must provide an explicit CELEX
identifier or URI. Article labels are optional and are stored only when
present in the source.

The importer does not resolve references over the network, infer missing
targets, or promote citations into stronger legal relationships.

References are deduplicated deterministically while preserving source order.
