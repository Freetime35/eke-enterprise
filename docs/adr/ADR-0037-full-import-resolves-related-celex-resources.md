# ADR-0037 — Full Import Resolves Related CELEX Resources

**Status:** Accepted

The full EUR-Lex import pipeline enriches a newly imported Resource with an
initial version, labeled EuroVoc classifications, relationships, and acquisition
provenance.

Because domain relationships point to internal `ResourceUUID` values, every
related CELEX identifier is resolved through the repository. When no Resource
exists, the import creates a minimal canonical target Resource in the same Unit
of Work. This avoids embedding external identifiers where internal identities
are required.

Only labeled EuroVoc concepts are mapped to `ClassificationConcept`. URI-only
concepts remain transport metadata until vocabulary enrichment supplies labels.
