# ADR-0059 — EUR-Lex Classification Import Is Limited to English Financial Concepts

**Status:** Accepted

The current product scope is banking, finance, financial institutions and
financial services. EUR-Lex classification projection is therefore limited to
English EuroVoc concepts whose labels match the explicit financial vocabulary.

The importer preserves source-backed scheme, broader and narrower URIs, but it
does not download or infer the complete EuroVoc hierarchy.

Non-English concepts and unrelated themes remain absent from the canonical
Resource classification collection. Their omission does not fail the import.

The selection vocabulary is deterministic and may be extended through reviewed
code changes when the product scope expands.
