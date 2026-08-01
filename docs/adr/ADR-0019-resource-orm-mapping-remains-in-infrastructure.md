# ADR-0019 — Resource ORM Mapping Remains in Infrastructure

**Status:** Accepted

## Context

The application requires durable Resource persistence while the domain must
remain independent of SQLAlchemy and database schemas.

## Decision

SQLAlchemy mappings, sessions, serialization, and database constraints SHALL
live exclusively under `eke.infrastructure`.

The initial adapter SHALL store each Resource aggregate as canonical JSON in a
`resources` table and maintain a normalized `resource_identifiers` search index.

The domain objects SHALL NOT inherit from ORM base classes or expose persistence
annotations.

## Consequences

### Positive

- The domain remains persistence-ignorant.
- Complete aggregates round-trip without ORM leakage.
- Business-identifier uniqueness is enforced by the database.
- SQLite and PostgreSQL-compatible SQLAlchemy APIs can share the adapter.

### Negative

- JSON payload fields are not independently queryable in this first adapter.
- Schema evolution requires payload migration strategy.
- Identifier index consistency depends on repository transactions.

## Alternatives considered

### Map every domain object directly as ORM entities

Rejected because it would tightly couple domain design to relational storage.

### Store only JSON without an identifier index

Rejected because repository lookup by business identifier would be inefficient
and database-dependent.
