# ADR-0057 — EUR-Lex Metadata Completeness Is Explicit and Source-Backed

**Status:** Accepted

EUR-Lex ingestion retains additional stable source metadata before
canonical mapping:

- ELI URI;
- CELLAR URI;
- Official Journal reference;
- responsible institution URIs;
- two-letter and supported three-letter language codes.

Completeness is assessed explicitly from ten stable fields. Missing
values remain missing; the importer does not invent defaults to improve
the score.

This PR enriches the transport-neutral metadata model. Canonical domain
projection of these values remains a separate concern.
