# ADR-0023 — FastAPI Is a Thin Presentation Adapter

**Status:** Accepted

## Context

The domain, application services, repositories, Unit of Work, SQLAlchemy,
and Alembic infrastructure are complete enough to expose an HTTP service.

The presentation framework must not become the location of business
rules or direct SQLAlchemy session management.

## Decision

FastAPI SHALL be introduced as a thin presentation adapter.

The HTTP application SHALL:

- be created through an application factory;
- assemble dependencies in a composition container;
- create ResourceService through UnitOfWork factories;
- apply database migrations during lifespan startup;
- dispose database resources during lifespan shutdown;
- expose process health and dependency readiness separately;
- read runtime values from immutable API settings;
- keep API routes independent of concrete repository implementations.

## Consequences

- Tests can create isolated applications with temporary databases.
- Business policies remain in the application and domain layers.
- The ASGI server and HTTP framework remain replaceable adapters.
- Startup fails early if migrations or database initialization fail.
- Later resource endpoints can depend on ResourceService without knowing
  SQLAlchemy.
