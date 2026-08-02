# ADR-0058 — EUR-Lex Relationships Are Imported Only When Targets Resolve

**Status:** Accepted

EUR-Lex CDM relationship predicates are mapped to the canonical
`RelationshipType` vocabulary during RDF/XML parsing.

A canonical relationship is persisted only when its target CELEX
already resolves to a canonical Resource in the current repository.
Unresolved targets do not create placeholder Resources and do not fail
the source import.

Duplicate source/type/target relationships are collapsed
deterministically. Unknown predicates and invalid CELEX targets are
ignored.

Deferred relationship resolution and recursive target import remain
outside this PR.
