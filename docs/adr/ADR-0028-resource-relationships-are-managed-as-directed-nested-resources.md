# ADR-0028 — Resource Relationships Are Managed as Directed Nested Resources

**Status:** Accepted

Resource relationships are directed and owned by their source Resource. The
Resource identified in the URL is always the source and the request supplies the
target.

Relationships are exposed under:

```text
/resources/{resource_uuid}/relationships
```

The target Resource must already exist. Relationship identity in the HTTP API is
the combination of target UUID, relationship type, valid-from, and valid-to.
Exact duplicates return 409 and missing relationships return 404.

All unrelated Resource aggregate data is preserved during relationship changes.
