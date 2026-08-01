# ADR-0026 — Resource Titles Are Managed as Nested API Resources

**Status:** Accepted

Resource titles are localized, temporal concepts owned by the Resource aggregate.

They are exposed under:

```text
/resources/{resource_uuid}/titles
```

A title is selected by language and validity boundaries. Duplicate titles return
409, missing titles return 404, and all unrelated aggregate state is preserved.
