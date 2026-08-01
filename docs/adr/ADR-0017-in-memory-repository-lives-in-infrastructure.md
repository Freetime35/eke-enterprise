# ADR-0017 — In-Memory Repository Lives in Infrastructure

**Status:** Accepted

## Context

The domain defines `ResourceRepository` as a structural persistence
contract.

Tests, local development, and early application services require a
concrete implementation before a production database adapter exists.

## Decision

EKE Enterprise SHALL provide `InMemoryResourceRepository` under the
infrastructure package.

The implementation SHALL:

- structurally satisfy `ResourceRepository`;
- store immutable Resource aggregates by ResourceUUID;
- replace existing aggregates on `save`;
- support lookup by ResourceUUID and BusinessIdentifier;
- support existence checks and deletion;
- expose `clear` and `count` as infrastructure conveniences;
- validate public input types;
- isolate state between repository instances;
- protect individual operations with a reentrant lock.

The implementation SHALL NOT be placed in the domain package.

## Consequences

### Positive

- Application services can be developed without a database.
- Tests can use a real repository implementation rather than mocks.
- Dependency direction remains correct.
- Repository state is deterministic and isolated.
- Individual operations are safe under concurrent access.

### Negative

- Data is not durable.
- Cross-operation transactions are not supported.
- Lookup by business identifier is linear.
- The implementation is not intended for production persistence.

## Alternatives considered

### Put the implementation in the domain package

Rejected because concrete storage behavior is infrastructure.

### Use a plain dictionary directly in tests

Rejected because it would bypass the repository contract and duplicate
behavior across tests.

### Delay implementation until a database is selected

Rejected because application-layer development benefits from an early
deterministic adapter.
