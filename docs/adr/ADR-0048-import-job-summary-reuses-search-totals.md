# ADR-0048 — Import Job Summary Reuses Search Totals

**Status:** Accepted

Import-job status totals are computed through the existing repository search
contract, requesting one item per status and reading each page's `total`.

This avoids expanding the runtime-checkable repository protocol again and
therefore avoids forcing every test double to implement another method.

The API exposes:

```text
GET /imports/eurlex/jobs/summary
```

The response includes the total job count and one count for every
`ImportJobStatus`.
