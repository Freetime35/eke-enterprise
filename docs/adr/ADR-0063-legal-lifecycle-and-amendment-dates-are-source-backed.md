# ADR-0063 — Legal Lifecycle and Amendment Dates Are Source-Backed

**Status:** Accepted

EUR-Lex lifecycle milestones are represented as immutable dated events that
retain the RDF predicate from which they were extracted.

The model supports document, adoption, signature, notification, publication,
entry into force, taking effect, application, transposition deadline, end of
validity, repeal and withdrawal events.

An amendment date is stored only when the source explicitly identifies the
amending CELEX, amended CELEX and effective date. Undated amendments remain
legal relationships and are not converted into dated events.

Events are deduplicated and sorted chronologically. Existing scalar metadata
dates remain available for backward compatibility.
