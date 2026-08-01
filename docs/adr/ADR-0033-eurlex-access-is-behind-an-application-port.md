# ADR-0033 — EUR-Lex Access Is Behind an Application Port

**Status:** Accepted

## Context

EKE Enterprise now models standard-form CELEX identifiers. The next ingestion
steps require retrieving official Publications Office payloads without coupling
application use cases to HTTPX, a concrete URL, or a specific metadata format.

EUR-Lex search web services use SOAP and require registration. The Publications
Office also exposes Cellar content and metadata through REST and persistent
resource identifiers.

## Decision

The application layer SHALL define an `EurLexClient` protocol that retrieves one
raw, transport-neutral `EurLexDocument` by `CelexIdentifier`.

The infrastructure layer SHALL provide `HttpxEurLexClient`, using the public
Publications Office CELEX resolver:

```text
https://publications.europa.eu/resource/celex/{celex}
```

The adapter SHALL:

- use HTTP content negotiation through `Accept`;
- follow redirects;
- preserve raw response bytes;
- record media type, final URL, and timezone-aware retrieval time;
- map 404 to `EurLexDocumentNotFoundError`;
- map transport and other HTTP failures to `EurLexUpstreamError`;
- accept an injected HTTPX client for deterministic tests.

Metadata parsing and Resource import SHALL remain separate future use cases.

## Consequences

- Application code is independent of HTTPX.
- Tests require no live EUR-Lex calls.
- RDF, XML, or other formats can be requested explicitly.
- Runtime deployment now includes HTTPX.
- Retrieval and metadata interpretation evolve independently.
