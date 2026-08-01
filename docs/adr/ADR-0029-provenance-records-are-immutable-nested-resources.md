# ADR-0029 — Provenance Records Are Immutable Nested Resources

**Status:** Accepted

Provenance records are immutable acquisition metadata owned by a Resource. They
are exposed under:

```text
/resources/{resource_uuid}/provenance
```

The domain provides no dedicated ProvenanceRecord UUID. HTTP deletion therefore
uses the complete functional identity:

- source;
- source reference;
- timezone-aware acquisition timestamp;
- acquisition method;
- optional checksum.

Exact duplicates return 409 and missing records return 404. Provenance changes
preserve all unrelated Resource aggregate data.
