# ADR-0077 — Legal Actors Are Derived from Explicit Rule Subjects

**Status:** Accepted

PR-082 derives legal actors only from subjects already present in
requirements-graph-backed compliance rules.

Actor identifiers are deterministic. One actor is created for each exact
normalized subject and optional linked definition. Mentions preserve the
originating requirement, node and source text.

Classification is limited to an explicit phrase table. A subject with one
linked definition is classified as `REGULATED_ENTITY`; otherwise an
unrecognized subject is `GENERIC_ACTOR`.

No synonym merging, translation, pronoun resolution, coordinated-subject
splitting, probabilistic named-entity recognition or LLM inference is
performed.
