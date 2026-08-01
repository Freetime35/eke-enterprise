# ADR-0018 — Resource Use Cases Live in an Application Service

**Status:** Accepted

## Context

The domain now defines Resource aggregates and a ResourceRepository
contract. Infrastructure provides an in-memory repository implementation.

The system needs orchestration for create, retrieve, update, and delete
use cases without placing workflow logic in the aggregate or repository.

## Decision

EKE Enterprise SHALL provide `ResourceService` in the application layer.

The service SHALL:

- depend only on `ResourceRepository`;
- create resources while preventing duplicate identity and business identifiers;
- retrieve resources by internal or business identifier;
- update only existing resources;
- reject identifiers owned by another resource during update;
- delete only existing resources;
- expose existence checks;
- translate missing and duplicate conditions into application exceptions.

The service SHALL NOT depend on concrete infrastructure implementations.

## Consequences

### Positive

- Use-case orchestration is centralized.
- Domain aggregates remain focused on business invariants.
- Infrastructure remains replaceable.
- Application errors are explicit and testable.
- The service can be reused by CLI, API, or batch adapters.

### Negative

- Transactions are not yet modeled.
- Concurrency conflicts are not addressed.
- Bulk operations are not included.
- Async use cases require future contracts.

## Alternatives considered

### Put CRUD methods on Resource

Rejected because persistence orchestration does not belong in the aggregate.

### Put duplicate checks inside repositories

Rejected because repositories provide storage behavior, while use-case
policies belong to the application layer.

### Depend directly on InMemoryResourceRepository

Rejected because application code must depend on the domain contract.
