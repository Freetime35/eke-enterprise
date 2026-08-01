# ADR-0030 — Resource Classifications Use Scheme-Code-Language Identity

**Status:** Accepted

Classification concepts are immutable value objects owned by the Resource
aggregate. They are exposed under:

```text
/resources/{resource_uuid}/classifications
```

The aggregate forbids repeated classification assignments with the same:

- classification scheme;
- stable concept code;
- label language.

The HTTP API therefore uses `(scheme, code, language)` as the assignment key.
The localized label and validity period remain attributes of that assignment.

Conflicting assignments return 409 and missing assignments return 404. All
unrelated Resource aggregate state is preserved.
