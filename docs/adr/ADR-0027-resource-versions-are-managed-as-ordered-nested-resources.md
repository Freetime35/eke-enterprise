# ADR-0027 — Resource Versions Are Managed as Ordered Nested Resources

**Status:** Accepted

Resource versions are owned by the Resource aggregate and are exposed under:

```text
/resources/{resource_uuid}/versions
```

The server generates each `version_uuid`. A `previous_version_uuid`, when
provided, must identify another version of the same Resource. A version that is
referenced by a successor cannot be deleted.

Version operations preserve every unrelated part of the Resource aggregate.
