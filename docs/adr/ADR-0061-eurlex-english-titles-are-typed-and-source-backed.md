# ADR-0061 — EUR-Lex English Titles Are Typed and Source-Backed

**Status:** Accepted

EUR-Lex title extraction retains only titles explicitly tagged as
English. Untagged and non-English titles are not projected.

Each retained title records its source role as `OFFICIAL`, `SHORT`,
`ALTERNATIVE`, or `UNKNOWN`. Predicate mapping is deterministic, title
whitespace is normalized, and exact typed duplicates are removed.

Existing construction remains compatible because `EurLexTitle.kind`
defaults to `UNKNOWN`.

The importer does not translate, abbreviate, or invent titles.
