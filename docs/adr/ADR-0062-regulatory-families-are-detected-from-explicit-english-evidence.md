# ADR-0062 — Regulatory Families Are Detected from Explicit English Evidence

**Status:** Accepted

Financial regulatory families are detected deterministically from:

- exact CELEX identifiers for reviewed foundational acts;
- explicit acronyms in English titles;
- unambiguous full English family names.

Detection does not use generic financial words, machine learning,
translation, or inferred thematic similarity. A document may match
multiple families, but each family is returned once and retains its
evidence kind and matched value.

The result remains transport-neutral metadata in this PR. Canonical
persistence and search by regulatory family are separate concerns.
