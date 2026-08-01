# PR-038 — EUR-Lex Client Port & HTTP Adapter

## Objective

Introduce a testable external-service boundary for retrieving official payloads
by CELEX identifier.

## Added

- `EurLexClient` application protocol;
- immutable `EurLexDocument`;
- EUR-Lex client exceptions;
- `HttpxEurLexClient`;
- configurable base URL and media type;
- HTTP error mapping;
- HTTPX MockTransport tests;
- ADR-0033.

## Dependency change

Move `httpx>=0.28,<1.0` from development-only dependencies to runtime
dependencies.

## Validation

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
python -m mypy
```

## Recommended commit

```text
feat(infrastructure): add EUR-Lex HTTP client
```
