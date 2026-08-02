# ADR-0067 — Legal Bases Are Explicit and Source-Backed

**Status:** Accepted

Legal bases are represented separately from generic legal references.

Each legal basis must retain its RDF predicate and identify an explicit URI
or CELEX target. Treaty, article, paragraph and label values are optional
and stored only when present in the source metadata.

The importer does not infer treaty articles from URI patterns, resolve legal
bases over the network, or extract bases from the full text of an act.

Duplicate legal bases are removed while preserving source order.
