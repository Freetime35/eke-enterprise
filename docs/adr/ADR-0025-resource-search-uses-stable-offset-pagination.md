# ADR-0025 — Resource Search Uses Stable Offset Pagination

**Status:** Accepted

## Context

The Resource API needs filtered collection retrieval without exposing
SQLAlchemy or database-specific query objects to the application layer.

## Decision

ResourceRepository SHALL expose a typed `search` operation using
`ResourceSearchCriteria` and returning `ResourceSearchPage`.

The first search contract supports:

- IdentifierScheme filtering;
- ResourceType filtering;
- ResourceStatus filtering;
- limit and offset pagination;
- stable ascending ordering by ResourceUUID;
- total count before pagination.

Limit SHALL be constrained to 1–100.

SQLAlchemy filtering MAY initially occur inside the infrastructure
adapter after aggregate decoding. Future optimization MAY push filters
into SQL without changing the repository contract.

## Consequences

- Application and HTTP layers remain database-independent.
- Pagination responses are deterministic.
- Both in-memory and SQLAlchemy adapters share one contract.
- Offset pagination is simple but may become inefficient for very deep
  pages.
- SQLAlchemy search performance is intentionally secondary to contract
  stability in this first version.
