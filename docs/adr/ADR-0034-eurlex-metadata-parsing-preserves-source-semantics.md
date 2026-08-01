# ADR-0034 — EUR-Lex Metadata Parsing Preserves Source Semantics

**Status:** Accepted

## Context

Cellar disseminates publication metadata as notices in RDF/XML or XML. Its
metadata model is based on the Common Data Model (CDM), while EKE Enterprise
uses source-independent domain enums and value objects.

Mapping every Cellar URI directly to EKE domain concepts inside the XML parser
would couple syntax parsing, source vocabulary interpretation, and Resource
construction.

## Decision

The application layer SHALL define:

- `EurLexMetadataParser`, a parser protocol;
- `EurLexMetadata`, a transport-neutral parsed representation;
- `EurLexTitle`, a localized title representation.

The infrastructure layer SHALL provide
`RdfXmlEurLexMetadataParser`, implemented with the Python standard library.

The parser SHALL extract only stable import inputs:

- CELEX identifier;
- localized titles;
- document, publication, entry-into-force, and end-of-validity dates;
- languages;
- source resource-type URI;
- source status URI;
- EuroVoc concept URIs.

Source vocabulary values SHALL remain URIs. Mapping them to `ResourceType`,
`ResourceStatus`, and classification objects belongs to a later import mapper.

The parser SHALL be namespace-tolerant by matching predicate local names, while
rejecting malformed XML, unsupported media types, invalid CELEX values, and a
CELEX mismatch with the requested document.

## Consequences

- XML syntax parsing remains independent from domain mapping.
- Unknown source vocabulary values are not lost.
- Parser tests use local fixtures and require no network.
- Future CDM mappings can evolve without rewriting the XML parser.
