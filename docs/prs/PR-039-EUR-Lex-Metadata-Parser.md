# PR-039 — EUR-Lex Metadata Parser

## Objective

Parse stable Cellar RDF/XML metadata into a transport-neutral application
model, ready for a later Resource import mapper.

## Added

- `EurLexMetadataParser` application protocol;
- immutable `EurLexMetadata` and `EurLexTitle`;
- metadata parsing exceptions;
- `RdfXmlEurLexMetadataParser`;
- CELEX consistency validation;
- localized title, date, language, source URI, and EuroVoc extraction;
- local RDF/XML fixture tests;
- ADR-0034.

## Scope boundary

This PR does not map Cellar URIs to EKE domain enums and does not create or
persist a `Resource`.

## Validation

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): parse EUR-Lex RDF metadata
```
