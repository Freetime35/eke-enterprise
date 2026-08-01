# ADR-0022 — Database Schema Evolves Through Alembic

**Status:** Accepted

## Context

SQLAlchemy mappings are now stable and migration-ready. Creating tables
directly through `Base.metadata.create_all()` is useful for isolated
tests, but it does not provide controlled schema evolution for deployed
databases.

## Decision

EKE Enterprise SHALL manage persistent database schema changes through
Alembic revision scripts.

The migration environment SHALL:

- use `Base.metadata` as autogeneration target metadata;
- support online and offline execution;
- use batch rendering for SQLite compatibility;
- permit programmatic execution through Alembic's command API;
- maintain reversible upgrade and downgrade functions.

The initial revision SHALL reproduce the current Resource persistence
schema, including deterministic constraint names and indexes.

## Consequences

- Database deployments become repeatable and versioned.
- Schema history is reviewable in Git.
- SQLite development and future PostgreSQL deployments share one
  migration mechanism.
- ORM metadata changes must be accompanied by explicit revisions.
- Production systems must run migrations before using newer code.
