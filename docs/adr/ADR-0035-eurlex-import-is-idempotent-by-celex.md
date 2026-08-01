# ADR-0035 — EUR-Lex Import Is Idempotent by CELEX

**Status:** Accepted

## Context

EKE Enterprise can retrieve official EUR-Lex payloads and parse stable Cellar
metadata. A workflow is now required to create canonical `Resource` aggregates
without duplicating a legal act when an import is retried.

`Resource` requires a business identifier and supports localized titles and
immutable provenance. `ClassificationConcept` additionally requires a localized
label, while the current metadata parser only exposes EuroVoc concept URIs.

## Decision

The application layer SHALL provide `EurLexResourceImportService`.

The import workflow SHALL:

1. resolve the CELEX business identifier in the repository;
2. return the existing Resource without an external request when found;
3. retrieve RDF/XML through `EurLexClient`;
4. parse metadata through `EurLexMetadataParser`;
5. map the payload to a new Resource;
6. re-check CELEX inside the same Unit of Work;
7. save and commit atomically;
8. return `EurLexImportResult(resource, created)`.

The mapper SHALL:

- use the CELEX identifier as the initial business identifier;
- map supported source type/status tokens conservatively;
- fall back to CELEX document type where appropriate;
- create titles only when a valid language is available;
- create one SHA-256 provenance record for the retrieved payload;
- leave relationships, versions, and classifications empty.

EuroVoc concepts SHALL not be converted to `ClassificationConcept` until labels
are available from a dedicated vocabulary enrichment capability.

## Consequences

- Repeated imports are idempotent by CELEX.
- Existing Resources are not silently overwritten.
- Fetching, parsing, mapping, and persistence remain independently testable.
- Unknown source semantics map to `OTHER` or `UNKNOWN`.
- EuroVoc enrichment remains an explicit future step.
