# ADR-0021 — SQLAlchemy Mappings Are Migration-Ready

**Status:** Accepted

## Context

The first SQLAlchemy adapter persisted complete Resource aggregates as
canonical JSON and maintained a relational business-identifier index.

Before introducing Alembic, the schema requires deterministic constraint
names, explicit indexes, technical timestamps, cascade behavior, and a
versioned payload format.

## Decision

Infrastructure mappings SHALL use a shared SQLAlchemy naming convention.

Resource rows SHALL contain:

- the aggregate UUID;
- a payload schema version;
- canonical JSON;
- creation and update timestamps.

Resource identifier rows SHALL be managed through an ORM relationship
with delete-orphan cascade.

The JSON codec SHALL use a versioned envelope and SHALL continue reading
legacy unversioned payloads.

## Consequences

- Alembic can generate stable migration names.
- Identifier replacement and deletion use ORM ownership semantics.
- Payload evolution has an explicit compatibility boundary.
- Existing version-zero payloads remain readable.
- Queryable aggregate fields remain intentionally limited to indexed
  infrastructure projections.
