# ADR-0039 — Import Jobs Are Persisted as Versioned Payloads

**Status:** Accepted

## Context

Import jobs require durable identity and state before execution services or an
HTTP API can be added. SQLite does not reliably preserve timezone information
from `DateTime(timezone=True)` values.

## Decision

The domain SHALL define immutable `ImportJob` and `ImportJobStatus` values.

The application layer SHALL define an `ImportJobRepository` protocol.

The SQLAlchemy adapter SHALL persist:

- job UUID;
- indexed status;
- payload version;
- complete JSON payload;
- database creation and update timestamps.

All domain timestamps SHALL be encoded as ISO 8601 values in the JSON payload.
This preserves timezone offsets exactly across SQLite and other databases.

PR-044 SHALL not add job execution or HTTP endpoints.

## Consequences

- Job persistence is independently testable.
- Future schema evolution can use payload versions.
- UTC and timezone offsets survive SQLite round trips.
- Execution and presentation remain separate later PRs.
