# ADR-0020 — Application Transactions Use Unit of Work

**Status:** Accepted

## Context

ResourceService previously depended directly on ResourceRepository. SQLAlchemy
persistence now requires explicit transaction boundaries spanning repository
operations and application policy checks.

## Decision

Application services SHALL depend on a factory producing `UnitOfWork` instances.

A UnitOfWork SHALL:

- expose a ResourceRepository through `resources`;
- define a context-manager lifecycle;
- provide explicit `commit()` and `rollback()`;
- roll back when an exception occurs;
- roll back when a write scope exits without commit.

Infrastructure SHALL provide in-memory and SQLAlchemy implementations.

## Consequences

- Application workflows are atomic.
- SQLAlchemy sessions remain infrastructure details.
- Tests can verify commit and rollback behavior without a database.
- Repositories can participate in one shared transaction.

The in-memory implementation uses snapshots and is intended for tests and local
development, not high-volume production workloads.
