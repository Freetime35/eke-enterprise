# ADR-0016 — Resource Persistence Is Defined by a Protocol

**Status:** Accepted

## Context

The domain model now contains a mature `Resource` aggregate with
identifiers, titles, versions, relationships, provenance, and
classifications.

Application services will need to load and persist resources without
coupling the domain to SQLAlchemy, Neo4j, an ORM, a web framework, or a
particular database.

## Decision

The domain SHALL define resource persistence through the structural
`ResourceRepository` protocol.

The contract SHALL expose:

- `save(Resource)`;
- `get(ResourceUUID)`;
- `get_by_identifier(BusinessIdentifier)`;
- `exists(ResourceUUID)`;
- `delete(ResourceUUID)`.

Missing lookups SHALL return `None`.

Deletion SHALL return a boolean indicating whether the resource
previously existed.

Repository implementations SHALL live outside the domain package.

## Consequences

### Positive

- The domain remains infrastructure-independent.
- In-memory and production implementations share one contract.
- Application services can depend on abstractions.
- Structural typing avoids mandatory inheritance.
- Tests can use lightweight fakes.

### Negative

- Transaction boundaries are not yet represented.
- Pagination and bulk operations are not included.
- Async persistence requires a separate future contract.
- Repository implementations must validate their own infrastructure
  failures and concurrency behavior.

## Alternatives considered

### Define an abstract base class

Rejected because nominal inheritance would unnecessarily constrain
implementations.

### Put repository interfaces in infrastructure

Rejected because dependency direction requires infrastructure to depend
on the domain contract.

### Raise an exception for missing resources

Rejected for the initial contract because optional lookup semantics are
simpler and explicit.
